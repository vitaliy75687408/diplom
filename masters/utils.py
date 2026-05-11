# -*- coding: utf-8 -*-
import os
try:
    import cv2
except ImportError:
    cv2 = None
import numpy as np


def _get_face_rect(user_img):
    """Повертає (x, y, w, h) першого знайденого обличчя або None."""
    if user_img is None or user_img.size == 0:
        return None
    try:
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        gray = cv2.cvtColor(user_img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.15, 5)
        if len(faces) == 0:
            return None
        x, y, w, h = faces[0]
        return (int(x), int(y), int(w), int(h))
    except Exception:
        return None


def apply_hair_overlay(user_img_path, hair_overlay_path):
    """
    Накладає PNG зачіски (з альфа-каналом) на фото користувача.
    Повертає BGR зображення (numpy array) або None при помилці.
    """
    user_img = cv2.imread(user_img_path)
    if user_img is None:
        return None
    hair = cv2.imread(hair_overlay_path, cv2.IMREAD_UNCHANGED)
    if hair is None:
        return None

    face = _get_face_rect(user_img)
    if face is None:
        return user_img

    x, y, w, h = face
    hair_width = int(w * 1.5)
    hair_height = int(h * 1.2)
    resized_hair = cv2.resize(hair, (hair_width, hair_height), interpolation=cv2.INTER_LINEAR)

    y_off = y - int(h * 0.35)
    x_off = x - int(w * 0.25)

    # Обрізаємо по межі кадру
    h_img, w_img = user_img.shape[:2]
    y1 = max(0, y_off)
    y2 = min(h_img, y_off + hair_height)
    x1 = max(0, x_off)
    x2 = min(w_img, x_off + hair_width)
    if y1 >= y2 or x1 >= x2:
        return user_img

    # Відповідні зони в resized_hair
    rh_y1 = y1 - y_off
    rh_y2 = rh_y1 + (y2 - y1)
    rh_x1 = x1 - x_off
    rh_x2 = rh_x1 + (x2 - x1)

    if resized_hair.ndim == 2:
        alpha = np.ones((resized_hair.shape[0], resized_hair.shape[1]), dtype=np.float32)
        hair_bgr = cv2.cvtColor(resized_hair, cv2.COLOR_GRAY2BGR)
    elif resized_hair.shape[2] == 4:
        alpha = (resized_hair[rh_y1:rh_y2, rh_x1:rh_x2, 3] / 255.0).astype(np.float32)
        hair_bgr = resized_hair[rh_y1:rh_y2, rh_x1:rh_x2, :3]
    else:
        alpha = np.ones((resized_hair.shape[0], resized_hair.shape[1]), dtype=np.float32) * 0.7
        hair_bgr = resized_hair[rh_y1:rh_y2, rh_x1:rh_x2, :3]

    roi = user_img[y1:y2, x1:x2]
    if roi.shape[:2] != hair_bgr.shape[:2]:
        return user_img
    alpha = np.expand_dims(alpha, axis=2)
    blended = (alpha * hair_bgr + (1 - alpha) * roi).astype(np.uint8)
    user_img[y1:y2, x1:x2] = blended
    return user_img


def apply_hairstyle_blend(user_img_path, style_image_path):
    """
    Накладає іншу зачіску (з фото стилю) на верх обличчя — щоб було видно саме НОВУ стрижку,
    а не свою. Сильний blend (92% нова зачіска), широка зона.
    """
    user_img = cv2.imread(user_img_path)
    if user_img is None:
        return None
    style_img = cv2.imread(style_image_path)
    if style_img is None:
        return None

    face = _get_face_rect(user_img)
    if face is None:
        return user_img

    x, y, w, h = face
    # Велика зона «нового волосся» — перекриває своє
    hair_w = int(w * 1.7)
    hair_h = int(h * 1.35)
    # Верхня половина фото стилю = чужа зачіска
    sh, sw = style_img.shape[:2]
    crop_top = style_img[0 : int(sh * 0.55), :]
    if crop_top.size == 0:
        return user_img
    resized = cv2.resize(crop_top, (hair_w, hair_h), interpolation=cv2.INTER_LINEAR)

    # Ставимо вище лоба, щоб покрити своє волосся
    y_off = y - int(h * 0.65)
    x_off = x - int(w * 0.35)
    h_img, w_img = user_img.shape[:2]

    y1 = max(0, y_off)
    y2 = min(h_img, y_off + hair_h)
    x1 = max(0, x_off)
    x2 = min(w_img, x_off + hair_w)
    if y1 >= y2 or x1 >= x2:
        return user_img

    rh_y1 = y1 - y_off
    rh_y2 = rh_y1 + (y2 - y1)
    rh_x1 = x1 - x_off
    rh_x2 = rh_x1 + (x2 - x1)
    patch = resized[rh_y1:rh_y2, rh_x1:rh_x2]
    roi = user_img[y1:y2, x1:x2]
    if patch.shape[:2] != roi.shape[:2]:
        return user_img
    # 92% — нова зачіска, 8% — фон: чітко видно іншу стрижку, не свою
    alpha = 0.92
    blended = (alpha * patch.astype(np.float32) + (1 - alpha) * roi.astype(np.float32)).astype(np.uint8)
    user_img[y1:y2, x1:x2] = blended
    return user_img
