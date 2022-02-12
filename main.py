from ursina import *
import numpy as np


class Values:
    array = np.array([])
    display_range = 13
    array_size = 30
    offset = display_range / array_size * 0.2
    bar_width = (display_range - offset * array_size) / array_size
    bars = []
    sorting = False
    finishing = False
    muted = True
    delay = 0
    comparisons = 0
    start_time = 0
    elapsed_time = 0
    pause_time = 0
    key_delay = 0
    buttons = []
    delay_slider = None
    size_slider = None
    comp_text = None
    elapsed_time_text = None
    sorting_alg = None
    sorting_gen = None
    finish_animation = None
    marked_button = None
    play_button = None
    mute_button = None
    mute_helper_text = None
    sfx = [(0.0, 0.0), (0.11, 0.0), (0.23, 0.64), (0.34, 0.0), (0.47, 0.0)]


def sfx(i):
    # this import didn't work any other way
    from ursina.prefabs.ursfx import ursfx
    if Values.muted:
        return
    pitch = (i / Values.array_size) * 25 - 4
    # having sounds enabled slows the program down to about 25%
    ursfx(Values.sfx, volume=0.75, wave='triangle', pitch=pitch, speed=0.9)


######################################################################################
############################# SORTING ALGORITHMS #####################################
######################################################################################

def bubble_sort():
    for i in range(Values.array_size - 1):
        for j in range(Values.array_size - i - 1):
            sfx(Values.array[j + 1])
            Values.comparisons += 1
            for _ in range(Values.delay + 1):
                yield j, j + 1
            if Values.array[j] > Values.array[j + 1]:
                Values.array[j], Values.array[j + 1] = Values.array[j + 1], Values.array[j]


def insertion_sort():
    for i in range(1, len(Values.array)):
        key = Values.array[i]
        j = i - 1
        while j >= 0 and key < Values.array[j]:
            Values.comparisons += 1
            Values.array[j + 1] = Values.array[j]
            j -= 1
            sfx(Values.array[j + 1])
            for _ in range(Values.delay + 1):
                yield i, j + 1
        Values.array[j + 1] = key


def selection_sort():
    for i in range(Values.array_size):
        min_idx = i
        for j in range(i + 1, Values.array_size):
            Values.comparisons += 1
            sfx(Values.array[j])
            yield None, j
            if Values.array[min_idx] > Values.array[j]:
                min_idx = j
                sfx(Values.array[j])
                for _ in range(Values.delay + 1):
                    yield j, None
        sfx(Values.array[min_idx])
        for _ in range(Values.delay + 1):
            yield i, min_idx
        Values.array[i], Values.array[min_idx] = Values.array[min_idx], Values.array[i]


# Note: Merge sort, heap sort and quick sort algorithms are iterative versions, as recursive algorithms don't work
# with the generator approach I took in this project
def merge_sort():
    low = 0
    high = Values.array_size - 1
    temp = Values.array.copy()
    m = 1
    while m <= high - low:
        Values.comparisons += 1
        for i in range(low, high, 2 * m):
            frm = i
            mid = i + m - 1
            to = min(i + 2 * m - 1, high)
            for _ in range(Values.delay + 1):
                yield frm, to
            k = frm
            i = frm
            j = mid + 1
            while i <= mid and j <= to:
                Values.comparisons += 1
                sfx(Values.array[i])
                for _ in range(Values.delay + 1):
                    yield i, j
                if Values.array[i] < Values.array[j]:
                    Values.comparisons += 1
                    temp[k] = Values.array[i]
                    i += 1
                else:
                    temp[k] = Values.array[j]
                    j += 1
                k += 1
            while i < Values.array_size and i <= mid:
                Values.comparisons += 1
                temp[k] = Values.array[i]
                k += 1
                i += 1
            for c in range(frm, to + 1):
                Values.array[c] = temp[c]
                sfx(Values.array[c])
                for _ in range(Values.delay + 1):
                    yield c, None
        m *= 2


def heap_sort():
    for i in range(Values.array_size):
        if Values.array[i] > Values.array[int((i - 1) / 2)]:
            Values.comparisons += 1
            sfx(Values.array[i])
            for _ in range(Values.delay + 1):
                yield i, int((i - 1) / 2)
            j = i
            while Values.array[j] > Values.array[int((j - 1) / 2)]:
                Values.comparisons += 1
                (Values.array[j],
                 Values.array[int((j - 1) / 2)]) = (Values.array[int((j - 1) / 2)],
                                                    Values.array[j])
                sfx(Values.array[i])
                for _ in range(Values.delay + 1):
                    yield i, int((i - 1) / 2)
                j = int((j - 1) / 2)
    for i in range(Values.array_size - 1, 0, -1):
        Values.array[0], Values.array[i] = Values.array[i], Values.array[0]
        sfx(Values.array[i])
        for _ in range(Values.delay + 1):
            yield 0, i
        j, index = 0, 0
        while True:
            index = 2 * j + 1
            Values.comparisons += 1
            if (index < (i - 1) and
                    Values.array[index] < Values.array[index + 1]):
                index += 1
            Values.comparisons += 1
            if index < i and Values.array[j] < Values.array[index]:
                sfx(Values.array[j])
                for _ in range(Values.delay + 1):
                    yield j, index
                Values.array[j], Values.array[index] = Values.array[index], Values.array[j]

            j = index
            if index >= i:
                break


def quick_sort():
    arr = Values.array
    l = 0
    h = Values.array_size - 1
    size = h - l + 1
    stack = [0] * size
    top = -1
    top += 1
    stack[top] = l
    top += 1
    stack[top] = h
    while top >= 0:
        Values.comparisons += 1
        h = stack[top]
        top -= 1
        l = stack[top]
        sfx(Values.array[h])
        for _ in range(Values.delay + 1):
            yield h, l
        top -= 1
        i = (l - 1)
        x = arr[h]
        for j in range(l, h):
            Values.comparisons += 1
            if arr[j] <= x:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
                sfx(Values.array[i])
                for _ in range(Values.delay + 1):
                    yield i, j
        sfx(Values.array[i + 1])
        for _ in range(Values.delay + 1):
            yield i + 1, h
        arr[i + 1], arr[h] = arr[h], arr[i + 1]
        p = i + 1
        for _ in range(Values.delay + 1):
            yield p, None
        Values.comparisons += 1
        if p - 1 > l:
            top += 1
            stack[top] = l
            top += 1
            stack[top] = p - 1
        Values.comparisons += 1
        if p + 1 < h:
            top += 1
            stack[top] = p + 1
            top += 1
            stack[top] = h


######################################################################################
######################################################################################
######################################################################################


def set_sorting_algorithm(algorithm):
    Values.sorting_alg = algorithm
    Values.sorting_gen = algorithm()
    Values.pause_time = 0


class Bar(Entity):
    def __init__(self, height, pos, bar_width):
        super().__init__(
            model="quad",
            color=color.peach,
            origin=(0, -0.5),
            scale=(bar_width, height),
            position=(pos, -4.1)
        )
        self.bar_width = bar_width
        self.height = height

    def set_height(self, new_height):
        self.scale = (self.bar_width, new_height)


class NormalButton(Button):
    BUTTON_COLOR = color.rgba(255, 218, 185, 150)
    BUTTON_HOVERED = color.rgba(238, 216, 196, 255)
    BUTTON_MARKED = color.peach

    def __init__(self, texture=None, algorithm=None, text_entity=None, *args, **kwargs):
        super().__init__(
            *args,
            **kwargs,
            parent=scene,
            model="quad",
            color=self.BUTTON_COLOR,
            highlight_color=self.BUTTON_HOVERED,
            highlight_scale=1.1,
            pressed_scale=1.1,
            texture=texture
        )
        self.text_entity = text_entity
        self.algorithm = algorithm

    def input(self, key):
        if self.hovered:
            if key == "left mouse down":
                self.algorithm()


class AlgorithmButton(NormalButton):
    def input(self, key):
        if self.hovered:
            if key == "left mouse down":
                set_sorting_algorithm(self.algorithm)
                Values.marked_button = self


class VisText(Text):
    def __init__(self, text, pos=(0, 0), scale=(1, 1), color=color.peach, **kwargs):
        super().__init__(
            text=text,
            color=color,
            scale=scale,
            position=pos,
        )


def set_array_size():
    if not Values.sorting and not Values.finishing:
        Values.array_size = Values.size_slider.value
        Values.offset = Values.display_range / Values.array_size * 0.2
        Values.bar_width = (Values.display_range - Values.offset * Values.array_size) / Values.array_size
        new_array()
        draw_array()


def set_delay():
    Values.delay = Values.delay_slider.value


def new_array():
    Values.array = np.arange(1, Values.array_size + 1)
    np.random.shuffle(Values.array)
    set_sorting_algorithm(Values.sorting_alg)
    return Values.array


def draw_array():
    for i in range(len(Values.bars)):
        destroy(Values.bars[i])
    Values.bars = []
    for i, num in enumerate(Values.array):
        Values.bars.append(Bar(height=get_height(num), pos=get_visual_pos(i), bar_width=Values.bar_width))


def update_array(marked_bar_1=None, marked_bar_2=None):
    for i, num in enumerate(Values.bars):
        new_height = get_height(Values.array[i])
        Values.bars[i].set_height(new_height)
        Values.bars[i].color = color.peach
    if marked_bar_1 is not None:
        Values.bars[int(marked_bar_1)].color = color.green
    if marked_bar_2 is not None:
        try:
            Values.bars[int(marked_bar_2)].color = color.red
        except IndexError:
            pass


def get_height(i):
    return i * (5 / Values.array_size)


def get_visual_pos(num):
    return -0.5 * Values.display_range + num * (Values.bar_width + Values.offset) + 0.5 * Values.bar_width


def finish_sort_animation():
    for i in range(len(Values.bars)):
        Values.bars[i].color = color.green
        sfx(Values.array[i])
        yield
    for _ in range(30):
        time.sleep(0.01)
        yield


def mark_button():
    for button in Values.buttons:
        if not button.hovered:
            button.color = NormalButton.BUTTON_COLOR
    Values.marked_button.color = NormalButton.BUTTON_MARKED


def toggle_sound():
    if Values.muted:
        Values.muted = False
        Values.mute_button.texture = "/assets/volume.png"
        Values.mute_helper_text.text = "SLOWER"
    else:
        Values.muted = True
        Values.mute_button.texture = "/assets/mute.png"
        Values.mute_helper_text.text = "FASTER"


def play_pause():
    if Values.sorting:
        Values.sorting = False
        Values.comparisons = 0
        Values.play_button.texture = "/assets/play.png"
        Values.pause_time = Values.elapsed_time
    elif Values.finishing:
        Values.play_button.texture = "/assets/pause.png"
    else:
        Values.sorting = True
        Values.finish_animation = finish_sort_animation()
        Values.play_button.texture = "/assets/pause.png"
        Values.start_time = time.perf_counter() - Values.pause_time


def update():
    if held_keys["space"] and Values.key_delay > 30:
        play_pause()
        Values.key_delay = 0
    elif held_keys["n"] and not Values.sorting:
        new_array()
    elif held_keys["esc"]:
        quit()
    if Values.sorting:
        try:
            pos1, pos2 = next(Values.sorting_gen)
            Values.elapsed_time = round(time.perf_counter() - Values.start_time, 2)
            update_array(pos1, pos2)
        except StopIteration:
            Values.sorting = False
            Values.finishing = True
            update_array()
    elif Values.finishing:
        try:
            next(Values.finish_animation)
        except StopIteration:
            Values.comparisons = 0
            Values.finishing = False
            Values.play_button.texture = "/assets/play.png"
            Values.pause_time = 0
    else:
        update_array()

    Values.key_delay += 1
    Values.comp_text.text = "Comparisons: " + str(Values.comparisons)
    Values.elapsed_time_text.text = str(Values.elapsed_time) + "s"
    mark_button()


def init():
    set_sorting_algorithm(bubble_sort)
    Values.array = new_array()
    draw_array()
    Text.size = 0.03
    Text.default_resolution = Text.size * 2000
    Values.size_slider = ThinSlider(
        dynamic=True,
        on_value_changed=set_array_size,
        min=2,
        max=150,
        default=30,
        step=1,
        scale=(0.7, 0.7),
        position=(-0.85, 0.45),
        color=color.peach
    )
    Values.size_slider_text = VisText(
        text="Array Size",
        pos=(-0.72, 0.48),
        scale=(0.5, 0.5),
    )
    Values.size_slider.knob.color = color.peach
    Values.size_slider.bg.color = color.peach
    Values.size_slider.knob.text_origin = (0, -0.04)
    Values.size_slider.knob.text_color = color.peach
    Values.size_slider.knob.scale = (0.82, 0.82)
    Values.delay_slider = ThinSlider(
        dynamic=True,
        on_value_changed=set_delay,
        min=0,
        max=50,
        default=0,
        step=1,
        scale=(0.7, 0.7),
        position=(-0.85, 0.37),
        color=color.peach
    )
    Values.delay_slider.knob.color = color.peach
    Values.delay_slider.bg.color = color.peach
    Values.delay_slider.knob.text_origin = (0, -0.04)
    Values.delay_slider.knob.text_color = color.peach
    Values.delay_slider.knob.scale = (0.82, 0.82)
    Values.delay_slider_text = VisText(
        text="Sorting Delay",
        pos=(-0.72, 0.4),
        scale=(0.5, 0.5)
    )
    Values.comp_text = VisText(
        text="0",
        pos=(0.65, 0.45),
        scale=(0.5, 0.5)
    )
    Values.elapsed_time_text = VisText(
        text="0",
        pos=(0.65, 0.4),
        scale=(0.5, 0.5)
    )
    Values.buttons.append(AlgorithmButton(
        scale=(1.2, 0.35),
        position=(-2.5, 3.4),
        algorithm=bubble_sort,
        text_entity=VisText(
            text="Bubble Sort",
            pos=(-0.365, 0.425),
            color=color.black90,
            scale=(0.7, 0.7),
        )
    ))
    Values.buttons.append(AlgorithmButton(
        scale=(1.2, 0.35),
        position=(-1.2, 3.4),
        algorithm=insertion_sort,
        text_entity=VisText(
            text="Insertion Sort",
            pos=(-0.212, 0.425),
            color=color.black90,
            scale=(0.7, 0.7),
        )
    ))
    Values.buttons.append(AlgorithmButton(
        scale=(1.2, 0.35),
        position=(0.1, 3.4),
        algorithm=selection_sort,
        text_entity=VisText(
            text="Selection Sort",
            pos=(-0.055, 0.425),
            color=color.black90,
            scale=(0.7, 0.7),
        )
    ))
    Values.buttons.append(AlgorithmButton(
        scale=(1.2, 0.35),
        position=(1.4, 3.4),
        algorithm=merge_sort,
        text_entity=VisText(
            text="Merge Sort",
            pos=(0.115, 0.425),
            color=color.black90,
            scale=(0.7, 0.7),
        )
    ))
    Values.buttons.append(AlgorithmButton(
        scale=(1.2, 0.35),
        position=(2.7, 3.4),
        algorithm=heap_sort,
        text_entity=VisText(
            text="Heap Sort",
            pos=(0.28, 0.425),
            color=color.black90,
            scale=(0.7, 0.7),
        )
    ))
    Values.buttons.append(AlgorithmButton(
        scale=(1.2, 0.35),
        position=(4, 3.4),
        algorithm=quick_sort,
        text_entity=VisText(
            text="Quick Sort",
            pos=(0.435, 0.425),
            color=color.black90,
            scale=(0.7, 0.7),
        )
    ))
    Values.play_button = NormalButton(
        scale=(0.5, 0.5),
        position=(-6.3, 2.4),
        algorithm=play_pause,
        texture='/assets/play.png'
    )
    Values.new_array_button = NormalButton(
        scale=(0.5, 0.5),
        position=(-5.5, 2.4),
        algorithm=new_array,
        texture='/assets/reset.png'
    )
    Values.mute_button = NormalButton(
        scale=(0.5, 0.5),
        position=(-4.7, 2.4),
        algorithm=toggle_sound,
        texture='/assets/mute.png'
    )
    Values.mute_helper_text = VisText(
        text="FASTER",
        pos=(-0.6, 0.25),
        scale=(0.4, 0.4),
        color=color.rgba(255, 218, 185, 150)
    )

    Values.marked_button = Values.buttons[0]


def main():
    app = Ursina()
    window.fps_counter.enabled = False
    window.borderless = False
    window.forced_aspect_ratio = 16 / 9
    init()
    destroy(window.exit_button)
    window.exit_button.enabled = False
    # this is to avoid lag when first playing any sound (as an import happens in the sfx() function)
    sfx(0)
    app.run()


if __name__ == "__main__":
    main()
