import numpy as np
import wave
from scipy.signal import medfilt
import matplotlib.pyplot as plt

def read_wav(file_name):
    with wave.open(file_name, 'rb') as wf:
        params = wf.getparams()
        frames = wf.readframes(params.nframes)
        data = np.frombuffer(frames, dtype=np.int16)
    return data, params

def write_wav(file_name, data, params):
    with wave.open(file_name, 'wb') as wf:
        wf.setparams(params)
        wf.writeframes(data.tobytes())

def moving_average(data, kernel_size):
    cumsum = np.cumsum(np.insert(data, 0, 0))
    return (cumsum[kernel_size:] - cumsum[:-kernel_size]) / kernel_size

input_file = 'input.wav'
output_file_combined = 'output_filtered_combined.wav'

try:
    # Загрузка аудиофайла
    data, params = read_wav(input_file)

    # Применение медианной фильтрации
    kernel_size = 3  # размер ядра фильтрации
    filtered_data_median = medfilt(data, kernel_size)

    # Применение фильтрации по среднему арифметическому к результату медианной фильтрации
    filtered_data_mean = moving_average(filtered_data_median, kernel_size)

    # Поскольку результат фильтрации по среднему арифметическому короче исходного массива, 
    # добавляем несколько нулевых значений в конец массива, чтобы выровнять их длину
    filtered_data_mean = np.pad(filtered_data_mean, (0, len(data) - len(filtered_data_mean)), 'constant')

    # Сохранение отфильтрованного аудиофайла
    write_wav(output_file_combined, filtered_data_mean.astype(np.int16), params)

    # Отображение исходного и отфильтрованного сигналов
    plt.figure(figsize=(12, 9))

    # Исходный сигнал
    plt.subplot(3, 1, 1)
    plt.plot(data, color='blue')
    plt.title('Исходный сигнал')
    plt.xlabel('Время [семплы]')
    plt.ylabel('Амплитуда')

    # Отфильтрованный сигнал (медианная фильтрация)
    plt.subplot(3, 1, 2)
    plt.plot(filtered_data_median, color='green')
    plt.title('Отфильтрованный сигнал (медианная фильтрация)')
    plt.xlabel('Время [семплы]')
    plt.ylabel('Амплитуда')

    # Отфильтрованный сигнал (медианная + среднее арифметическое)
    plt.subplot(3, 1, 3)
    plt.plot(filtered_data_mean, color='red')
    plt.title('Отфильтрованный сигнал (медианная + среднее арифметическое)')
    plt.xlabel('Время [семплы]')
    plt.ylabel('Амплитуда')

    # Показать графики
    plt.tight_layout()
    plt.show()

    print(f'Файл сохранен как {output_file_combined}')

except FileNotFoundError:
    print(f"Файл '{input_file}' не найден. Убедитесь, что файл существует в указанном пути.")
except wave.Error as e:
    print(f"Ошибка при открытии файла '{input_file}': {e}")
except Exception as e:
    print(f"Произошла ошибка: {e}")
