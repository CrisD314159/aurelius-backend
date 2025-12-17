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

    def __init__(self, databse: AureliusDB):
        self.db_context: AureliusDB = databse
        self.tts_model = TTSKokoroService()
        self.messages = []

    async def assemble_prompt(self, user_prompt, websocket: WebSocket):
        """
        retrieves all the user context and generates the prompt for the llm
        """
        user_model = self.db_context.get_user_model()
        user_context_dict = self.retrieve_user_context()
        if len(self.messages) == 0:
            self.messages.append(user_context_dict)
        else:
            self.messages[0] = user_context_dict

        self.messages += [
            {
                "role": "user",
                "content": user_prompt
            }
        ]

        await self.generate_response(user_model, websocket=websocket)

        return True

    async def generate_response(self, model, websocket: WebSocket):
        """
        Generates the llm response for the user using chunks and the TTS model provided
        """
        try:

            response: Iterator[ChatResponse] = chat(model=model, messages=self.messages,
                                                    stream=True)
            response_buffer = ""
            entire_response = ""

            sentence_separator = re.compile(
                r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|!)\s+')

            context: Mapping[str, Any] | None = None

            for chunk in response:
                response_text = chunk.message.content
                entire_response += response_text
                response_buffer += response_text
                parts = sentence_separator.split(response_buffer)
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

            if context is not None:
                self.save_new_context(context=context)
        except Exception as e:
            print(e)
            await socket_exeption_handling(ws=websocket, error_type="error",
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

    def generate_and_extract_context(self, answer, user_message, model):

        messages_internal = [
            {"role": "system", "content": """
            Based on the last user prompt and your reply, use the the provided 'save_new_context' function tool to generate information that should be stored for future context and user understanding
            .Ensure the input is a list of tuples (Example: [("favorite_artist", "Michael Jackson"), ("other_key", "other_value"), ...]). Its information that will help you to understand the user better
             and deliver more accurate answers
        """},
            {"role": "assistant", "content": answer},
            {"role": "user", "content": user_message}
        ]
        response_private: Iterator[ChatResponse] = chat(
            model=model, messages=messages_internal, stream=True, tools=[self.save_new_context])

        context = []

        for chunk in response_private:
            if chunk.message.tool_calls:
                for tool_call in chunk.message.tool_calls:
                    if tool_call.function.name == "save_context":
                        context = tool_call.function.arguments
        self.save_new_context(context=context)

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
             3. If you need to store new data about the user, use the provided tool 'save_new_context' providing a list of tuples using key - value syntax.
             4. Please do not use emojis or asterisks on your answers.
               """
        }

        return user_context_message
