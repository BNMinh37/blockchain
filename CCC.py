import tkinter as tk
from tkinter import messagebox
import hashlib, time, json, qrcode
import os

# ==== Cấu trúc block và blockchain ====
class Block:
    def __init__(self, index, data, previous_hash):
        self.index = index
        self.timestamp = time.time()
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps({
            'index': self.index,
            'timestamp': self.timestamp,
            'data': self.data,
            'previous_hash': self.previous_hash
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

class Blockchain:
    #def __init__(self):
     #   self.chain = [self.create_genesis_block()]
    def __init__(self, filename="blockchain_data.json"):
        self.filename = filename
        self.chain = []

        if os.path.exists(self.filename):
            self.load_from_file()
        else:
            self.chain = [self.create_genesis_block()]
            self.save_to_file()


    def create_genesis_block(self):
        return Block(0, "Genesis Block", "0")

    def add_block(self, data):
        previous_block = self.chain[-1]
        new_block = Block(len(self.chain), data, previous_block.hash)
        self.chain.append(new_block)

    def get_latest_block(self):
        return self.chain[-1]

    def save_to_file(self, filename="blockchain_data.json"):
        chain_data = []
        for block in self.chain:
            chain_data.append({
                'index': block.index,
                'timestamp': block.timestamp,
                'data': block.data,
                'previous_hash': block.previous_hash,
                'hash': block.hash
            })
        with open(filename, "w") as f:
            json.dump(chain_data, f, indent=4)

    def load_from_file(self):
        with open(self.filename, "r") as f:
            chain_data = json.load(f)
            self.chain = []
            for block in chain_data:
                blk = Block(
                    index=block['index'],
                    data=block['data'],
                    previous_hash=block['previous_hash']
                )
                blk.timestamp = block['timestamp']
                blk.hash = block['hash']  # giữ nguyên hash đã tạo
                self.chain.append(blk)

# ==== Giao diện người dùng ====
class App:
    def __init__(self, root):
        self.blockchain = Blockchain()

        root.title("Hệ thống cấp chứng chỉ Blockchain")

        tk.Label(root, text="Họ tên sinh viên").grid(row=0, column=0)
        tk.Label(root, text="Tên khóa học").grid(row=1, column=0)
        tk.Label(root, text="Tổ chức cấp").grid(row=2, column=0)
        tk.Label(root, text="Ngày cấp (YYYY-MM-DD)").grid(row=3, column=0)

        self.name_entry = tk.Entry(root, width=40)
        self.course_entry = tk.Entry(root, width=40)
        self.inst_entry = tk.Entry(root, width=40)
        self.date_entry = tk.Entry(root, width=40)

        self.name_entry.grid(row=0, column=1)
        self.course_entry.grid(row=1, column=1)
        self.inst_entry.grid(row=2, column=1)
        self.date_entry.grid(row=3, column=1)

        tk.Button(root, text="Cấp chứng chỉ & tạo mã QR", command=self.issue_certificate).grid(row=4, column=0, columnspan=2, pady=10)

    def issue_certificate(self):
        data = {
            "student": self.name_entry.get(),
            "course": self.course_entry.get(),
            "institution": self.inst_entry.get(),
            "issue_date": self.date_entry.get()
        }

        if "" in data.values():
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ thông tin.")
            return

        self.blockchain.add_block(data)
        self.blockchain.save_to_file()

        last_hash = self.blockchain.get_latest_block().hash
        #qr = qrcode.make(f"Verify certificate: {last_hash}")
        #qr.save("static/certificate_qr.png")

        os.makedirs("static", exist_ok=True)

        # Tạo QR code
        qr_text = f"Verify certificate: {last_hash}"
        qr = qrcode.make(qr_text)

        # Đặt tên file QR theo hash (lấy 10 ký tự đầu cho gọn)
        filename = f"qr_{last_hash[:10]}.png"
        filepath = os.path.join("static", filename)
        qr.save(filepath)

        messagebox.showinfo("Thành công", f"Chứng chỉ đã ghi vào blockchain.\nMã QR lưu tại {filepath}")
        #messagebox.showinfo("Thành công", f"Chứng chỉ đã được ghi vào blockchain.\nMã QR đã lưu thành certificate_qr.png")

# ==== Chạy ứng dụng ====
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
