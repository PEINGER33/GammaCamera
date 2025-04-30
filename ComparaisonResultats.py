import SimpleITK as sitk
import numpy as np
import cv2
import matplotlib.pyplot as plt
from skimage.metrics import structural_similarity as ssim

def normalize(img):
    return cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

def compute_snr(signal, noise):
    signal_power = np.mean(signal ** 2)
    noise_power = np.mean(noise ** 2)
    if noise_power == 0:
        return float('inf')
    return 10 * np.log10(signal_power / noise_power)

def compare_images(dcm_path, mhd_path, dcm_slice_idx):
    # Charger image simulée
    sim = sitk.ReadImage(mhd_path)
    sim_np = normalize(sitk.GetArrayFromImage(sim)[0])  # slice 0
    sim_np = cv2.rotate(sim_np, cv2.ROTATE_180)  # Rotation 180°

    # Charger image réelle
    real = sitk.ReadImage(dcm_path)
    real_np = normalize(sitk.GetArrayFromImage(real)[dcm_slice_idx])

    # Crop haut/bas
    crop_top = 20
    crop_bottom = 20
    sim_np = sim_np[crop_top:-crop_bottom, :]
    real_np = real_np[crop_top:-crop_bottom, :]

    # Resize si nécessaire
    if sim_np.shape != real_np.shape:
        sim_np = cv2.resize(sim_np, (real_np.shape[1], real_np.shape[0]))

    # Calculs
    ssim_val = ssim(real_np, sim_np)
    mse_val = np.mean((real_np - sim_np) ** 2)
    snr_val = compute_snr(real_np, real_np - sim_np)

    # === Affichage seulement des images normales ===
    fig, axs = plt.subplots(1, 2, figsize=(12, 5))

    axs[0].imshow(real_np, cmap='gray')
    axs[0].set_title('Image Réel')
    axs[0].axis('on')

    axs[1].imshow(sim_np, cmap='gray')
    axs[1].set_title(f'Image Simulé\nSSIM={ssim_val:.3f}, MSE={mse_val:.1f}, SNR={snr_val:.2f} dB')
    axs[1].axis('on')

    plt.tight_layout()
    plt.show()

# === Exemple d'utilisation ===

slice_number = 73

compare_images(
    dcm_path="C:/Users/TAS/Desktop/MissionRD/Zip/wetransfer_donnees-fantome-nema_2025-03-28_1624/TOMONEMA_EM_IRACSCRR001_DS.dcm",
    mhd_path="C:/Users/TAS/Desktop/MissionRD/output/output/projection_back__10e4Bq_10e5ev__docker_21.mhd",
    dcm_slice_idx=slice_number
)
