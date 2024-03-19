import struct
import zlib
import sys
from rich import print as rich_print
from rich.progress import Progress
import os


# PNG 文件的魔数（Magic Number）
PNG_MAGIC_NUMBER = b"\x89PNG\r\n\x1A\n"


def read_png_info(file_path):
    """ 获取png信息 """
    with open(file_path, "rb") as file:
        # 使用前8个字节进行判断是否为png格式的文件
        binary_data = file.read()
    if binary_data[:8] != PNG_MAGIC_NUMBER:
        print('不是png文件,无法处理,退出程序')
        sys.exit()
    ihdr = binary_data[12:29] # IHDR除CRC外全部部分
    origin_crc = binary_data[29:33] # IHDR 的 CRC 部分
    return ihdr, origin_crc, binary_data
    
def crack_ihdr_crc(ihdr: bytes, origin_crc: bytes, binary_data: bytes, current_path: str, out_filename: str):
    """ 根据正确的CRC值爆破ihdr的宽高 """
    ihdr_data = bytearray(ihdr)
    origin_crc_int_value = int.from_bytes(origin_crc, byteorder="big")
    origin_width = bytearray(ihdr_data[4:8])
    origin_height = bytearray(ihdr_data[8:12])
    n = 4096    # 实际上分辨率基本不会超过该值
    rich_print(f"[*] 原宽: {int.from_bytes(origin_width, byteorder='big')} (0x{origin_width.hex().upper()}) 原高: {int.from_bytes(origin_height, byteorder='big')} (0x{origin_height.hex().upper()})")

    with Progress() as progress:
        task = progress.add_task("[green]爆破IHDR CRC对应宽高...", total=n)
        for w in range(n):
            width = bytearray(struct.pack(">i", w))
            for h in range(n):
                height = bytearray(struct.pack(">i", h))
                for i in range(4):
                    ihdr_data[i+4] = width[i]
                    ihdr_data[i+8] = height[i]
                crc32_calc_value = zlib.crc32(ihdr_data)
                if crc32_calc_value == origin_crc_int_value:
                    progress.update(task, completed=n, description="[green]Processing completed")
                    rich_print(f"[green][+] 宽为: {int.from_bytes(width, byteorder='big')} (0x{width.hex().upper()}) 高为: {int.from_bytes(height, byteorder='big')} (0x{height.hex().upper()})  符合CRC: 0x{origin_crc.hex().upper()}[/green]")
                    rewrite_png(width, height, binary_data, current_path, out_filename)
                    sys.exit()
            progress.update(task, advance=1, description=f"[green]Processing item {i+1}")
        
    rich_print(f"[-] [red]没有找到符合CRC: 0x{origin_crc.hex().upper()}值对应的宽高[/red]")

def rewrite_png(width: bytearray, height: bytearray, binary_data: bytes, current_path: str, out_filename: str):
    """ 将爆破出来的正确宽高重新生成到新文件 """
    binary_bytearray = bytearray(binary_data)
    binary_bytearray[16:20] = width
    binary_bytearray[20:24] = height
    with open(os.path.join(current_path, out_filename), 'wb') as f:
        f.write(bytes(binary_bytearray))
    
    rich_print(f"[*] 文件保存到: [green]{os.path.join(current_path, out_filename)}[/green]")
    
    
if __name__ == '__main__':
    # 输出文件名
    # 获取当前工作路径
    current_path = os.getcwd()
    out_filename = "out.png"
    filename = "dabai.png"
    ihdr, origin_crc, binary_data = read_png_info(filename)
    crack_ihdr_crc(ihdr, origin_crc, binary_data)