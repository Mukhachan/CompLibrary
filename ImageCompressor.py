from PIL import Image
import os

class ImageCompressor:

    def compress_image(input_path, output_path, max_size_mb = 1):
        """Сжимает изображение в форматах PNG, JPEG или WEBP с помощью библиотеки Pillow.
        Исходное изображение находится в файле input_path, сжатая версия сохраняется в файл output_path.
        Максимальный размер файла в мегабайтах задается параметром max_size_mb."""

        # Загружаем исходное изображение из input_path
        
        with Image.open(input_path) as image:
            
            # Вычисляем максимальный размер файла в байтах
            max_size_bytes = max_size_mb * 1024 * 1024
            
            # Сжимаем изображение, пока его размер не станет меньше или равным максимальному размеру
            while os.path.getsize(input_path) > max_size_bytes:
                
                # Уменьшаем качество изображения на 10%
                quality = int(image.info.get('quality', 80) * 0.9)
                
                # Сохраняем сжатую версию изображения в файл output_path
                image.save(output_path, format=image.format, quality=quality)
                
                # Загружаем сжатую версию изображения и перезаписываем исходное изображение
                with Image.open(output_path) as compressed_image:
                    image = compressed_image.copy()
        
            # Сохраняем финальную версию сжатого изображения в файл output_path
            image.save(output_path, format=image.format, quality=quality)
            print('Изображение сохранено с выходным размером:', os.path.getsize(input_path))

input_path = 'static/pictures/' + '39158380.webp'
output_path = 'static/pictures/' + '39158380.webp'

ImageCompressor.compress_image(input_path, output_path)
