
# Görsel Şifreleme Projesi

Bu proje, (3,3) Görsel Şifreleme yöntemini kullanarak bir görüntüyü üç farklı şeffaf paya böler ve bu payları birleştirerek orijinal görüntüyü tekrar oluşturmayı amaçlar. Şifreleme işlemi sırasında görüntü siyah-beyaz formatına dönüştürülür ve görsel şifreleme algoritması uygulanır.


## Proje İçeriği ve Kullanımı
Proje, aşağıdaki adımları içerir:
 - Giriş görüntüsünün işlenmesi
 - Görüntünün dither (siyah-beyaz) formatına dönüştürülmesi
 - Üç adet şeffaf payın oluşturulması
 - Payların birleştirilmesi
 - Oluşan görüntülerin PNG formatında kaydedilmesi


## Kullanım

Projenin çalıştırılması için input_image.png adlı bir görüntü dosyasının proje dizininde bulunması gerekmektedir. Bu dosya, şifreleme işleminin giriş görüntüsü olacaktır.
Proje, şu komutla çalıştırılabilir:

```bash
python visual_cryptography.py
```

Bu komut, aşağıdaki işlemleri gerçekleştirecektir:
## Kod Açıklamaları

#### VisualCryptography Sınıfı

Bu sınıf, tüm işlemleri gerçekleştirmek için gerekli yöntemleri içerir. Sınıfın constructor kısmında kullanılan pixel matrisleri, siyah ve beyaz pixeller için desenleri belirtir.

```python
self.pixel_matrix = {
    '0': [  # Beyaz piksel için
        [[1,1,0,0]], [[1,0,1,0]], [[1,0,0,1]],
        [[0,1,1,0]], [[0,1,0,1]], [[0,0,1,1]]
    ],
    '1': [  # Siyah piksel için
        [[1,1,0,0]], [[1,0,1,0]], [[1,0,0,1]],
        [[0,1,1,0]], [[0,1,0,1]], [[0,0,1,1]]
    ]
}
```

#### Görüntünün Kontrastının Artırılması

**enhance_image** fonksiyonu, giriş görüntüsünün kontrastını artırarak daha net bir görüntü oluşturur.

```python
def enhance_image(self, image):
    enhancer = ImageEnhance.Contrast(image)
    enhanced_image = enhancer.enhance(2.0)
    return enhanced_image

```

#### Dither İşlemi

Görüntüyü siyah-beyaz formata dönüştürmek için Floyd-Steinberg dither algoritması kullanılır.

```python
def floyd_steinberg_dither(self, image):
    img_array = np.array(image)
    threshold = 128
    return Image.fromarray(((img_array > threshold) * 255).astype(np.uint8))
```

#### Payların Oluşturulması

**generate_shares** fonksiyonu, görüntünün piksel değerlerini 2x2 alt desenlere bölerek üç ayrı şeffaf pay oluşturur.

```python
def generate_shares(self, image):
    width = image.width * 2
    height = image.height * 2
    shares = [np.zeros((height, width, 4), dtype=np.uint8) for _ in range(3)]
    binary_image = np.array(image) // 255
    # Piksel bazlı şifreleme işlemleri
    return [Image.fromarray(share, 'RGBA') for share in shares]
```

#### Payların Birleştirilmesi

**combine_shares** fonksiyonu, tüm payları birleştirerek orijinal görüntüyü tekrar oluşturur.

```python
def combine_shares(self, shares):
    width, height = shares[0].size
    combined = Image.new('RGBA', (width, height), (255,255,255,255))
    for x in range(width):
        for y in range(height):
            pixels = [np.array(share.getpixel((x, y))) for share in shares]
            is_black = any(p[3] > 0 for p in pixels)
            if is_black:
                combined.putpixel((x, y), (0, 0, 0, 255))
    return combined
```

#### Ana İşlem Akışı

**process_image** fonksiyonu, tüm işlemleri sırasıyla gerçekleştirerek şifreli görüntüyü oluşturur.


```python
def process_image(self, input_path):
    image = Image.open(input_path).convert('L')
    enhanced_image = self.enhance_image(image)
    dithered = self.floyd_steinberg_dither(enhanced_image)
    shares = self.generate_shares(dithered)
    for idx, share in enumerate(shares):
        share.save(f'share_{idx+1}.png', 'PNG')
    combined = self.combine_shares(shares)
    combined.save('combined_shares.png', 'PNG')
    dithered.save('dithered.png')
```

## Üretilen Dosyalar

Kod çalıştırıldığında aşağıdaki dosyalar oluşturulacaktır:

 - **share_1.png**, **share_2.png**, **share_3.png**: Üç şeffaf pay
 - **dithered.png**: Siyah-beyaz dönüştürülmüş giriş görüntüsü
 - **combined_shares.png**: Payların birleştirilmesiyle oluşan görüntü
## Gereksinimler

 - Python 3.7+
 - Pillow kütüphanesi
 - NumPy

 Kurulum için:

 ```bash
 pip install pillow numpy
 ```
