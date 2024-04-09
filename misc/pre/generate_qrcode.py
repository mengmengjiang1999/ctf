import qrcode

data="flag{fak3_fl@9_ple@s3_v!slt_bilibili_video_BV1Jg4y1P76p}"

qr= qrcode.QRCode(version=1, box_size=1, border=1, error_correction=qrcode.constants.ERROR_CORRECT_H)
qr.add_data(data)
qr.make(fit=True)
qr_img=qr.make_image(fill_color="black", back_color="white")
qr_img.save("qr.jpg")