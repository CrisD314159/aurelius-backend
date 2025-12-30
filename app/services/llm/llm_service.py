"""
This module contains a class designed to handle all the services related with llm
"""

import re
from typing import Iterator
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

        if chat_id != self.current_chat:
            self.current_chat = chat_id
            self.messages[0] = user_context_dict
            chat_messages = self.db_context.get_chat_content_ollama(
                chat_id=chat_id)
            self.messages += chat_messages

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

            for chunk in response:
                response_text = chunk.message.content
                answer += response_text

            self.messages += [
                {'role': 'assistant', 'content': answer},
            ]

            await self.store_and_send_interaction(
                self.messages[-2], answer, websocket=websocket)

        except (ConnectionError, TimeoutError, ValueError, RuntimeError) as e:
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

            for chunk in response:
                response_text = chunk.message.content
                entire_response += response_text
                response_buffer += response_text
                parts = self.sentence_separator.split(response_buffer)
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

            await self.store_and_send_interaction(
                self.messages[-2], entire_response, websocket=websocket)

        except (ConnectionError, TimeoutError, ValueError, RuntimeError) as e:
            await socket_exeption_handling(
                ws=websocket, error_type="error",
                message="An error occured on LLM Service, try to open Ollama",
                details=str(e))

    async def store_and_send_interaction(self,
                                         user_prompt,
                                         llm_answer,
                                         websocket: WebSocket):
        """
        Stores a new interaction of a chat onto the local database
        """
        user_message = user_prompt['content']

        if self.current_chat == 0:
            title = f"{user_message[:30]}..."
            print("Titulo de nuevo chat", title)
            new_chat_id = self.db_context.create_chat(title=title)
            self.current_chat = new_chat_id

        interaction_info = self.db_context.store_interaction(
            chat_id=self.current_chat, user_prompt=user_message, llm_answer=llm_answer)

        await websocket.send_json({
            "message": interaction_info,
            "type": "answer"
        })

    def retrieve_user_context(self):
        """
        Retrieves the user stored context
        """
        user_data = self.db_context.get_user_data()
        user_name = "Not provided"
        if user_data:
            name, model = user_data
            user_name = name
        user_context_message = {
            "role": "system",
            "content": f"""
            
            As an intelligent assistant called Aurelius you are going to provide 
            clear, helpful and reliable responses To the user.
             User name: {user_name}

             Important rules: 
             1. Always use this information to enhance context, continuity and personalization.
             2. Do not reveal this information to the user.
             3. If you need to store data from the user, USE the provided tool 'save_new_context' providing a list of strings. Example: ["User likes strawberries", ...].
             4. Please do not use emojis or asterisks on your answers. Answer ONLY using Markdown
             5. If you include code in your answer, use triple backticks and indicate de language
               """
        }

        return user_context_message
