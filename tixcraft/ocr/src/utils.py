import string

# 支援小寫 a~z
CHARACTER_SET = list(string.ascii_lowercase)

char2idx = {
    char: idx + 1 for idx, char in enumerate(CHARACTER_SET)
}  # idx=0 給 CTC 的 blank
idx2char = {idx: char for char, idx in char2idx.items()}


def decode_prediction(pred_tensor):
    """
    CTC 解碼：去除重複與 blank=0
    """
    decoded = []
    for seq in pred_tensor.argmax(2).permute(1, 0):
        text = ""
        prev = -1
        for idx in seq:
            idx = idx.item()
            if idx != prev and idx != 0:
                text += idx2char.get(idx, "")
            prev = idx
        decoded.append(text)
    return decoded
