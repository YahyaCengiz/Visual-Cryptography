import numpy as np
from PIL import Image
import random
from PIL import ImageEnhance

class VisualCryptography:
    def __init__(self):
        """(3,3) görsel şifreleme için sınıf başlatıcı"""
        self.pixel_matrix = {
            '0': [  # Beyaz piksel için olasılıklar
                [[1,1,0,0]], [[1,0,1,0]], [[1,0,0,1]],
                [[0,1,1,0]], [[0,1,0,1]], [[0,0,1,1]]
            ],
            '1': [  # Siyah piksel için olasılıklar
                [[1,1,0,0]], [[1,0,1,0]], [[1,0,0,1]],
                [[0,1,1,0]], [[0,1,0,1]], [[0,0,1,1]]
            ]
        }

    def floyd_steinberg_dither(self, image):
        """
        Görüntüyü önce grayscale'a çevirir ve sonra Floyd-Steinberg dithering uygular
        """
        # Görüntüyü grayscale'a çevir
        grayscale = image.convert('L')
        
        # Grayscale görüntüyü numpy dizisine çevir
        img_array = np.array(grayscale, dtype=float)
        height, width = img_array.shape
        
        # Floyd-Steinberg dithering
        for y in range(height-1):
            for x in range(width-1):
                old_pixel = img_array[y, x]
                new_pixel = 255 if old_pixel > 127 else 0
                img_array[y, x] = new_pixel
                
                error = old_pixel - new_pixel
                
                # Hata dağıtımı
                if x + 1 < width:
                    img_array[y, x+1] += error * 7/16
                if y + 1 < height:
                    if x > 0:
                        img_array[y+1, x-1] += error * 3/16
                    img_array[y+1, x] += error * 5/16
                    if x + 1 < width:
                        img_array[y+1, x+1] += error * 1/16
        
        # Grayscale görüntüyü kaydet
        grayscale.save('grayscale.png')
        
        # Dither edilmiş görüntüyü oluştur ve döndür
        dithered = Image.fromarray(np.uint8(img_array))
        return dithered

    def generate_shares(self, image):
        """3 adet şeffaf pay görüntüsü oluşturur"""
        width = image.width * 2
        height = image.height * 2
        
        # RGBA formatında 3 pay oluştur
        shares = [np.zeros((height, width, 4), dtype=np.uint8) for _ in range(3)]
        binary_image = np.array(image) // 255

        for y in range(image.height):
            for x in range(image.width):
                y2, x2 = y*2, x*2
                
                if binary_image[y, x] == 0:  # Siyah piksel
                    pattern1 = random.choice(self.pixel_matrix['1'])[0]
                    pattern2 = random.choice(self.pixel_matrix['1'])[0]
                    pattern3 = random.choice(self.pixel_matrix['1'])[0]
                else:  # Beyaz piksel
                    pattern1 = random.choice(self.pixel_matrix['0'])[0]
                    pattern2 = np.logical_not(pattern1).astype(int)
                    pattern3 = random.choice(self.pixel_matrix['0'])[0]

                # Her pay için 2x2 alt pikselleri ayarla
                for idx, pattern in enumerate([pattern1, pattern2, pattern3]):
                    for i in range(2):
                        for j in range(2):
                            pixel_idx = i * 2 + j
                            alpha_value = 255 if pattern[pixel_idx] else 0
                            shares[idx][y2+i,x2+j] = [0,0,0,alpha_value]

        return [Image.fromarray(share, 'RGBA') for share in shares]

    def combine_shares(self, shares):
        """Payları birleştirerek final görüntüyü oluşturur"""
        width, height = shares[0].size
        combined = Image.new('RGBA', (width, height), (255,255,255,255))
        
        # Tüm pikselleri kontrol et
        for x in range(width):
            for y in range(height):
                # Her paydan pikselleri al
                pixels = [np.array(share.getpixel((x, y))) for share in shares]
                
                # Eğer herhangi bir payda siyah piksel varsa, final görüntüde siyah olacak
                is_black = any(p[3] > 0 for p in pixels)
                
                if is_black:
                    combined.putpixel((x, y), (0, 0, 0, 255))
                else:
                    combined.putpixel((x, y), (255, 255, 255, 255))
        
        return combined

    def enhance_image(self, image):
        # Görüntü netliğini artırmak için kontrastı artırabiliriz
        enhancer = ImageEnhance.Contrast(image)
        enhanced_image = enhancer.enhance(2.0)  # Kontrastı artır
        return enhanced_image

    def process_image(self, input_path):
        """Görüntüyü işler ve şeffaf payları oluşturur"""
        # Görüntüyü yükle
        image = Image.open(input_path)
        
        # Dither işlemi uygula (içinde grayscale dönüşümü de var)
        dithered = self.floyd_steinberg_dither(image)
        
        # Payları oluştur
        shares = self.generate_shares(dithered)
        
        # Payları PNG formatında kaydet
        for idx, share in enumerate(shares):
            share.save(f'share_{idx+1}.png', 'PNG')
        
        # Payları birleştir ve kaydet
        combined = self.combine_shares(shares)
        combined.save('combined_shares.png', 'PNG')
        
        # Dither edilmiş görüntüyü kaydet
        dithered.save('dithered.png')

def main():
    vc = VisualCryptography()
    vc.process_image('input_image.png')  # Giriş görüntüsünün yolunu belirtin

if __name__ == "__main__":
    main()
