from lib.ihdr_crc import read_png_info, crack_ihdr_crc
from lib.banner import BANNER

import os
import argparse
from rich import print as rich_print

# 创建 ArgumentParser 对象
parser = argparse.ArgumentParser(description='Explode the width and height of png images based on CRC value')

# 添加必选参数
parser.add_argument('-i', '--image', type=str, required=True,
                    help='input image file path')

# 添加可选参数
parser.add_argument('-o', '--output', type=str,
                    help='output image file path')

# 解析命令行参数
args = parser.parse_args()

current_path = os.getcwd()


if not os.path.exists(args.image):
    rich_print(f"[red][-][/red] 路径 {args.image} 不存在, 请检查路径")

rich_print(f"[green]{BANNER}[/green]")

# 处理解析后的参数
if args.output:
    ihdr, origin_crc, binary_data = read_png_info(args.image)
    crack_ihdr_crc(ihdr, origin_crc, binary_data, current_path)
else:
    out_filename = "out.png"
    ihdr, origin_crc, binary_data = read_png_info(args.image)
    crack_ihdr_crc(ihdr, origin_crc, binary_data, current_path, out_filename)