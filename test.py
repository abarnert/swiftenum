from swiftenum import SwiftEnum

class Barcode(SwiftEnum):
    upca = (int, int, int, int)
    qrcode = (str)

barcode1 = Barcode.upca(8, 85909, 51226, 3)
barcode2 = Barcode.qrcode('ABCDEFGHIJKLMNOP')

def handle(barcode):
    if barcode.name == 'upca':
        number_system, manufacturer, product, check = barcode
        print('UPC-A: {number_system}, {manufacturer}, {product}, {check}'
              .format_map(locals()))
    elif barcode.name == 'qrcode':
        product_code, = barcode
        print('QR code: {product_code}'.format_map(locals()))

handle(barcode1)
handle(barcode2)
