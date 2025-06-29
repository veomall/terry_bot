import os
import base64
import tempfile
import traceback
from logger_setup import logger
from g4f.client import AsyncClient

async def get_ai_response(provider_name, model, messages, image_bytes=None):
    """Get response from AI model using g4f."""
    try:
        # Создаем AsyncClient
        client = AsyncClient()
        logger.debug(f"Created AsyncClient for {provider_name}/{model}")
        
        # Подготавливаем запрос в зависимости от наличия изображения
        if image_bytes:
            try:
                # Для работы с изображениями используем base64 кодирование
                # Конвертируем байты изображения в base64
                base64_image = base64.b64encode(image_bytes).decode('utf-8')
                logger.debug(f"Encoded image to base64, size: {len(base64_image)}")
                
                # Формируем содержимое сообщения с изображением
                # Используем формат с изображением в content
                last_message = messages[-1]
                image_message = {
                    "role": last_message["role"],
                    "content": [
                        {"type": "text", "text": last_message["content"]},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
                
                # Заменяем последнее сообщение на версию с изображением
                messages_with_image = messages[:-1] + [image_message]
                
                logger.info(f"Sending request to {provider_name}/{model} with image")
                
                # Отправляем запрос с изображением
                response = await client.chat.completions.create(
                    model=model,
                    messages=messages_with_image,
                    provider=provider_name,
                    stream=False
                )
            except Exception as img_err:
                logger.warning(f"Error using content format for image: {str(img_err)}. Trying alternative method...")
                
                # Сохраняем изображение во временный файл
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
                    temp_file.write(image_bytes)
                    temp_path = temp_file.name
                
                logger.debug(f"Saved image to temporary file: {temp_path}")
                
                try:
                    # Пытаемся использовать файл вместо BytesIO
                    with open(temp_path, "rb") as img_file:
                        logger.info(f"Sending request to {provider_name}/{model} with image file")
                        response = await client.chat.completions.create(
                            model=model,
                            messages=messages,
                            provider=provider_name,
                            image=img_file,
                            stream=False
                        )
                finally:
                    # Удаляем временный файл
                    try:
                        os.unlink(temp_path)
                        logger.debug(f"Deleted temporary file: {temp_path}")
                    except Exception as e:
                        logger.warning(f"Failed to delete temp file {temp_path}: {str(e)}")
        else:
            # Обычный текстовый запрос
            logger.info(f"Sending text request to {provider_name}/{model} with {len(messages)} messages")
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                provider=provider_name,
                stream=False
            )
        
        # Извлекаем текст ответа
        result = response.choices[0].message.content
        logger.debug(f"Received response from {provider_name}/{model}, length: {len(result)}")
        return result
        
    except Exception as e:
        logger.error(f"Error getting response from {provider_name}/{model}: {str(e)}")
        logger.debug(traceback.format_exc())
        raise

async def generate_image(provider_name, model, prompt):
    """Generate image using g4f."""
    try:
        logger.info(f"Generating image with {provider_name}/{model}, prompt: '{prompt[:50]}...'")
        client = AsyncClient()
    
        response = await client.images.generate(
            prompt=prompt,
            model=model,
            # provider=provider_name,
            provider=None,
            response_format="url"
        )
        image_url = response.data[0].url
        
        logger.debug(f"Generated image URL: {image_url}")
        return image_url
        
    except Exception as e:
        logger.error(f"Error generating image with {model}: {str(e)}")
        logger.debug(traceback.format_exc())
        raise Exception(f"Не удалось сгенерировать изображение: {str(e)}") 