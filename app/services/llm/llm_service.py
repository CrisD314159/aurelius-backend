"""
This module contains a class designed to handle all the services related with llm
"""

import re
from typing import Iterator, Mapping, Any
from fastapi import WebSocket
from ollama import chat, ChatResponse
from app.db.init_db import AureliusDB
from app.services.tts.tts_kokoro_service import TTSKokoroService
from app.exceptions.exception_handling import socket_exeption_handling


class LLMService:
    """
    Integrates all the code to handle requests and answers from the llm
    """

    def __init__(self):
        self.db_context = AureliusDB()
        self.tts_model = TTSKokoroService()
        self.sentence_separator = re.compile(
            r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|!)\s+')
        self.messages = []
        self.current_chat = 0

    async def assemble_prompt(self, user_prompt,
                              websocket: WebSocket,
                              chat_id: int,
                              use_voice: bool):
        """
        retrieves all the user context and generates the prompt for the llm
        """

        user_model = self.db_context.get_user_model()
        user_context_dict = self.retrieve_user_context()
        if len(self.messages) == 0:
            self.messages.append(user_context_dict)
        else:
            self.messages[0] = user_context_dict

        if chat_id != 0:
            self.current_chat = chat_id
            current_messages = self.db_context.get_chat_content(
                chat_id=chat_id)
            self.messages += current_messages

        self.messages += [
            {
                "role": "user",
                "content": user_prompt
            }
        ]

        if use_voice:
            await self.generate_response_voice_mode(user_model, websocket=websocket)
        else:
            await self.generate_response_text_mode(user_model, websocket=websocket)

        return True

    async def generate_response_text_mode(self, model, websocket: WebSocket):
        """
        Generates the llm response for the user using chunks and the TTS model provided
        """
        try:

            response: Iterator[ChatResponse] = chat(model=model, messages=self.messages,
                                                    stream=True)
            answer = ""

            context: Mapping[str, Any] | None = None

            for chunk in response:
                response_text = chunk.message.content
                answer += response_text
                if chunk.message.tool_calls:
                    print(chunk.message.tool_calls)
                    for tool_call in chunk.message.tool_calls:
                        if tool_call.function.name == "save_context":
                            context = tool_call.function.arguments

            self.messages += [
                {'role': 'assistant', 'content': answer},
            ]

            self.store_and_send_interaction(
                self.messages[-1], answer, model=model, websocket=websocket)

            if context is not None:
                self.save_new_context(context=context)
        except (ConnectionError, TimeoutError, ValueError, RuntimeError) as e:
            print(e)
            await socket_exeption_handling(
                ws=websocket, error_type="error",
                message="An error occured on LLM Service, try to open Ollama",
                details=str(e))

    async def generate_response_voice_mode(self, model, websocket: WebSocket):
        """
        Generates the llm response for the user using chunks and the TTS model provided
        """
        try:

            response: Iterator[ChatResponse] = chat(model=model, messages=self.messages,
                                                    stream=True)
            response_buffer = ""
            entire_response = ""

            context: Mapping[str, Any] | None = None

            for chunk in response:
                response_text = chunk.message.content
                entire_response += response_text
                response_buffer += response_text
                parts = self.sentence_separator.split(response_buffer)
                if chunk.message.tool_calls:
                    print(chunk.message.tool_calls)
                    for tool_call in chunk.message.tool_calls:
                        if tool_call.function.name == "save_context":
                            context = tool_call.function.arguments
                if len(parts) > 1:
                    for sentence in parts[:-1]:
                        if sentence.strip() and len(sentence.strip()) > 3:
                            await self.tts_model.stream_audio_response(
                                websocket=websocket, text=sentence)

                    response_buffer = parts[-1]

            if response_buffer.strip():
                await self.tts_model.stream_audio_response(
                    websocket=websocket, text=response_buffer)

            self.messages += [
                {'role': 'assistant', 'content': entire_response},
            ]

            self.store_and_send_interaction(
                self.messages[-1], entire_response, model=model, websocket=websocket)

            if context is not None:
                self.save_new_context(context=context)
        except (ConnectionError, TimeoutError, ValueError, RuntimeError) as e:
            await socket_exeption_handling(
                ws=websocket, error_type="error",
                message="An error occured on LLM Service, try to open Ollama",
                details=str(e))

    def save_new_context(self, context):
        """
        This method receives and stores new context variable for aurelius personalization
        """
        print("Nuevo contexto", context)
        # if len(context) > 0:
        #     for memory_val in context:
        #         print(f" saved {memory_val[0]}, {memory_val[1]}")
        #         self.db_context.save_memory(
        #             key=memory_val[0], value=memory_val[1])

    def store_and_send_interaction(self, user_prompt, llm_answer, model, websocket: WebSocket):
        """
        Stores a new interaction of a chat onto the local database
        """
        user_message = user_prompt['content']

        if self.current_chat == 0:
            response = chat(model=model, messages=[
                {"role": "system",
                    "content": """Suggest a title for this chat, 
                    give only the title in one line (40 chars max)"""},
                user_prompt,
                {"role": "assistant", "content": llm_answer}
            ], stream=False)
            title = response['message']['content']
            print(title)
            new_chat_id = self.db_context.create_chat(title=title)
            self.current_chat = new_chat_id

        interaction_info = self.db_context.store_interaction(
            chat_id=self.current_chat, user_prompt=user_message, llm_answer=llm_answer)

        websocket.send_json({
            "message": interaction_info,
            "type": "answer"
        })

    def retrieve_user_context(self):
        """
        Retrieves the user stored context
        """
        user_context_dict = self.db_context.load_memory()
        user_data = self.db_context.get_user_data()
        user_name = "Not provided"
        if user_data:
            name, model = user_data
            user_name = name

        memory_lines = "\n".join(
            f"- {key.replace('_', ' ')}: {value}"
            for key, value in user_context_dict.items()
        )
        user_context_message = {
            "role": "system",
            "content": f"""
            User context store data:
            As an intelligent assistant called Aurelius you are going to provide 
            clear, helpful and reliable responses using user's stored data.

             User name: {user_name}

             User stored data:

             {memory_lines}

             Important rules: 
             1. Always use this information to enhance context, continuity and personalization.
             2. Do not reveal this information to the user.
             3. If you need to store new data about the user, use the provided tool 'save_new_context' providing a list of strings. Example: ["User likes strawberries", ...].
             4. Please do not use emojis or asterisks on your answers.
               """
        }

        return user_context_message
