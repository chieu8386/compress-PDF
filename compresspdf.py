import os
import glob
import tkinter as tk
from tkinter import messagebox
import fitz  # Thư viện PyMuPDF

def compress_pdfs(input_path, output_path, target_size=800):
    file_size = os.path.getsize(input_path) / 1024
    
    # 1. Nếu file nhỏ hơn mục tiêu -> Giữ nguyên để bảo toàn chất lượng
    if file_size <= target_size:
        doc = fitz.open(input_path)
        doc.save(output_path, garbage=4, deflate=True)
        doc.close()
        return f"Không nén vì {file_size:.1f} KB <= {target_size} KB"
        
    src_doc = fitz.open(input_path)
    new_doc = fitz.open()
    
    # Duyệt qua từng trang của file PDF
    for page in src_doc:
        # CÂN BẰNG ĐỘ PHÂN GIẢI: Dùng Matrix(2.0, 2.0) ~ 144 DPI giúp chữ nét, không vỡ nét
        pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
        
        # GIẢI PHÁP XÓA VIỀN XÁM: Quay lại JPG nhưng nâng chất lượng lên 75% 
        # Mức 75% xóa sạch bóng mờ xung quanh chữ mảnh, giữ nền trắng tinh khôi nhưng file vẫn rất nhẹ
        img_bytes = pix.tobytes(output="jpg", jpg_quality=75)
        
        # Tạo trang mới trống có kích thước tương đương trang cũ
        new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
        
        # Vẽ bức ảnh JPG chất lượng cao đè khít lên trang mới
        new_page.insert_image(page.rect, stream=img_bytes)
        
    src_doc.close()

    # 3. Lưu file và kích hoạt thuật toán tối ưu hóa hệ thống
    new_doc.save(
        output_path, 
        garbage=4,       # Loại bỏ hoàn toàn cấu trúc rác
        deflate=True,    # Nén chặt luồng nhị phân
        clean=True       # Làm sạch cây thư mục đối tượng PDF
    )
    new_doc.close()
    
    final_size = os.path.getsize(output_path) / 1024
    return f"Đã nén tối ưu cân bằng: {file_size:.1f} KB -> {final_size:.1f} KB"

def main():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    
    input_folder = "input_folder"
    output_folder = "output_folder"
    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)
    
    pdf_files = glob.glob(os.path.join(input_folder, "*.pdf"))
    
    if not pdf_files:
        messagebox.showinfo("Thông báo", "Chưa có PDF file trong input_folder")
        root.destroy()
        return
        
    report_messages = []
    for file_path in pdf_files:
        filename = os.path.basename(file_path)
        output_path = os.path.join(output_folder, f"Đã nén PDF {filename}")
        try:
            result_status = compress_pdfs(file_path, output_path)
            report_messages.append(f"- {filename}: {result_status}")
        except Exception as e:
            report_messages.append(f"- {filename}: Lỗi ({str(e)})")
            
    thong_bao = "Hoàn tất nén PDF\n\n" + "\n".join(report_messages)
    messagebox.showinfo("Kết quả nén PDF", thong_bao)
    root.destroy()

if __name__ == "__main__":
    main()