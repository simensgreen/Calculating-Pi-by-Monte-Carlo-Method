from tkinter import Tk, Canvas
from random import randint
from math import pi


class RandomPoints:
    points_options = {
        'fill': 'lime',
        'outline': 'green',
    }

    canvas_points_ids = []
    drawed_points = 0

    def __init__(self, canvas: Canvas, amount=10, radius=5):
        self.radius = radius
        self.canvas = canvas
        self.amount = amount

    def draw(self):
        for current_point in range(self.amount):
            coords = self.random_coords
            self.canvas_points_ids.append(self.canvas.create_oval(*coords, coords[0] + self.radius,
                                                                  coords[1] + self.radius, **self.points_options))
            self.drawed_points += 1

    @property
    def random_coords(self):
        return randint(0, int(self.canvas['width'])), randint(0, int(self.canvas['height']))


class App:
    canvas_animation_options = {
        'width': 720,
        'height': 720,
        'bg': '#2B2B2B'
    }

    canvas_data_options = {
        'width': 420,
        'height': 500,
        'bg': '#2B2B2B'
    }

    canvas_chart_options = {
        'width': 420,
        'height': 220,
        'bg': '#2B2B2B'
    }

    quarter_circle_options = {
        'start': 0,
        'extent': -90,
        'width': 2,
        'outline': 'gray',
        'fill': '#3C3F41'
    }

    chart = None
    chart_factor = 1

    _all_lists = {
        '_canvas_points_ids': [],
        '_canvas_data_ids': [],
        '_canvas_middle_line_ids': [],
        '_canvas_data_middle_line_ids': [],
        '_canvas_text_ids': [],
        '_caught_points': set(),
        '_canvas_text_math_error_id': [],
        '_all_values_pi': []
    }

    _quarter_circle_descriptor = 0
    canvas_size_error = 3
    amount_points = 100
    multiplicity = 10000
    coord_y_for_table = 70

    def __init__(self):
        self.root = Tk()

        # Полотно с математической моделью:
        self.animation_canvas = Canvas(self.root, **self.canvas_animation_options)
        self.animation_canvas.pack(side='left')

        # Полотно с исследуемыми данными:
        self.data_canvas = Canvas(self.root, **self.canvas_data_options)
        self.data_canvas.pack()

        # Полотно с диаграммой:
        self.chart_canvas = Canvas(self.root, **self.canvas_chart_options)
        self.chart_canvas.pack(side='bottom')

        self.draw_stationary_objects()
        self._physics_process()
        self._process()

    def draw_stationary_objects(self):
        """
        Отрисовка всех неподвижных объектов
        """
        self._quarter_circle_descriptor = self._draw_quarter_circle()
        self.print_data_about_pi_line()
        self.draw_pi_line()
        self.draw_table()

    def _draw_quarter_circle(self):
        """
        Отрисовка четверти круга
        Returns: дескриптор четверти круга
        """
        quarter_circle_descriptor = self.animation_canvas.create_arc(
            -self.canvas_animation_options['width'],
            -self.canvas_animation_options['height'],
            self.canvas_animation_options['width'],
            self.canvas_animation_options['height'],
            **self.quarter_circle_options)
        return quarter_circle_descriptor

    def print_data_about_pi_line(self):
        """
        Печать точного значения числа pi.
        """
        self.chart_canvas.create_text(100 + self.canvas_chart_options['width'] // 4,
                                      30, text=f'Истинное pi = {pi}', font=('Comic Sans MS', 15), fill='#648658')

    def draw_pi_line(self):
        """
        Отрисовка линии, которая соответствует точному значению числа pi.
        """
        self.chart_canvas.create_line(0, (pi / 4) * 130,
                                      self.canvas_chart_options['width'],
                                      (pi / 4) * 130,
                                      fill='#499C54')

    def draw_table(self):
        for coord_x in range(self.canvas_data_options['width'] // 3,
                             self.canvas_data_options['width'],
                             self.canvas_data_options['width'] // 3):
            self.data_canvas.create_line(coord_x, 0, coord_x, self.canvas_data_options['height'], fill='#AFB9BA')

        for coord_y in range(self.canvas_data_options['height'] // 11,
                             self.canvas_data_options['height'],
                             self.canvas_data_options['height'] // 11):
            self.data_canvas.create_line(0, coord_y, self.canvas_data_options['width'], coord_y, fill='#AFB9BA')

        self.data_canvas.create_text(70, 25, text='Кол-во точек', font=('Comic Sans MS', 15), fill='#AFB9BA')
        self.data_canvas.create_text(210, 25, text='Число pi', font=('Comic Sans MS', 15), fill='#AFB9BA')
        self.data_canvas.create_text(350, 25, text='Погрешность', font=('Comic Sans MS', 15), fill='#AFB9BA')
        # for i in range(70, 500, 45):
        #     self.data_canvas.create_text(350, i, text='Погрешность', font=('Comic Sans MS', 15), fill='#AFB9BA')

    def _physics_process(self):
        """
        Создание экземпляра класса Point, т.е. создаётся
        конечное множество рандомно расположенных на полотне точек определённого цвета.
        """
        self.points = RandomPoints(self.animation_canvas, self.amount_points)
        self.points.points_options['fill'] = '#ECBB06'
        self.points.points_options['outline'] = '#ECBB06'

    def _process(self):
        self.update_math_error()
        self.update_middle_line()
        self.update_data_middle_line()
        self.update_other_values_data_on_chart_canvas()
        process = self.root.after(100, self._process)

        self._draw_points()
        self._paint_points()
        self.print_math_error()
        self.draw_current_value_line()
        self.print_data_about_middle_line()
        self.print_other_data_on_chart_canvas()
        self.draw_chart((self.points.drawed_points, self.count_probability * 130))
        if self.points.drawed_points <= self.multiplicity * 10:
            self.fill_table()
        self.stop_process(process)

    def update_middle_line(self):
        """
        Обновить среднюю линию.
        """
        self.clean_canvas('_canvas_middle_line_ids')

    def update_data_middle_line(self):
        """
        Обновление данных, стоящих рядом со средней линией
        """
        self.clean_canvas('_canvas_data_middle_line_ids')

    def update_other_values_data_on_chart_canvas(self):
        self.clean_canvas('_canvas_text_ids')

    def update_math_error(self):
        self.clean_canvas('_canvas_text_math_error_id')

    def _draw_points(self):
        """
        Рисовать точки
        """
        self.points.draw()
        while len(self.points.canvas_points_ids) > 500:
            self.animation_canvas.delete(self.points.canvas_points_ids.pop(0))

    def _paint_points(self):
        """
        Перекрашывает точки, которые пересклись с кругом
        """
        for point in self.points.canvas_points_ids:
            point_coord = self.animation_canvas.coords(point)
            if point_coord[0] ** 2 + point_coord[1] ** 2 <= (self.canvas_animation_options['height']) ** 2:
                self.animation_canvas.itemconfig(point, fill='#4096C1', outline='#4096C1')
                self._all_lists['_caught_points'].add(point)

    def print_math_error(self):
        self._all_lists['_canvas_text_math_error_id'] = [
            self.chart_canvas.create_text(100 + self.canvas_chart_options['width'] // 4,
                                          60,
                                          text=f'Поргрешность:'
                                               f' {abs(round(100 * (1 - pi / (4 * self.count_probability)), 5))} %',
                                          font=('Comic Sans MS', 15), fill='#648658')]

    def draw_current_value_line(self):
        """
        Отрисовка текущей линии, абсциса кординат которой
        соответствует значению вероятности попадания точек в круг
        """
        self._all_lists['_canvas_middle_line_ids'] = [self.chart_canvas.create_line(0, self.count_probability * 130,
                                                                                    self.canvas_chart_options['width'],
                                                                                    self.count_probability * 130,
                                                                                    fill='#ECBB06')]

    def print_data_about_middle_line(self):
        """
        Печатать нужную информацию рядом со средней линией.
        В данном случае печатается текущее значение числа pi.
        """
        self._all_lists['_canvas_data_middle_line_ids'] = [
            self.chart_canvas.create_text(3 * self.canvas_data_options['width'] // 4,
                                          10 + self.count_probability * 130,
                                          text=f'{round(4 * self.count_probability, 5)}',
                                          font=('Comic Sans MS', 15),
                                          fill='#ECBB06')]

        # print(f'Вероятность: {self.count_probability()}')
        # print(f'Число pi: {4 * self.count_probability()}')

    def print_other_data_on_chart_canvas(self):
        self._all_lists['_canvas_text_ids'] = [
            self.chart_canvas.create_text(self.canvas_chart_options['width'] // 2,
                                          (4 * self.canvas_chart_options['height']) // 6 + 25,
                                          text=f'Общее число точек: {self.points.drawed_points}\n'
                                               f'    Точки в круге: {len(self._all_lists["_caught_points"])}',
                                          font=('Comic Sans MS', 15),
                                          fill='#AFB9BA')]

    def draw_chart(self, coordinates):
        """
        Отрисовка диаграммы
        Args:
            coordinates:
        """

        def scale_coordinates(coords):
            """Скалирует координаты по оси x"""
            for no, coord in enumerate(coords):
                yield coord * self.chart_factor if no % 2 == 0 else coord

        if self.chart is None:
            self.chart = self.chart_canvas.create_line(coordinates,
                                                       coordinates[0] + 4, coordinates[1] + 4,
                                                       fill='#4096C1', width=4)
        else:
            old_coords = self.chart_canvas.coords(self.chart)
            scaled_coordinates = scale_coordinates(coordinates)
            if self.chart_canvas.coords(self.chart)[-2] >= self.chart_canvas.winfo_width() - 100:
                self.chart_factor /= 2
                old_coords = list(scale_coordinates(old_coords))
            self.chart_canvas.coords(self.chart, *(old_coords + list(scaled_coordinates)))

    def fill_table(self):
        if self.points.drawed_points % self.multiplicity == 0:
            self.data_canvas.create_text(70, self.coord_y_for_table, text=f'{self.points.drawed_points}',
                                         font=('Comic Sans MS', 15), fill='#AFB9BA')
            self.data_canvas.create_text(210, self.coord_y_for_table, text=f'{round(4 * self.count_probability, 7)}',
                                         font=('Comic Sans MS', 15), fill='#AFB9BA')
            self.data_canvas.create_text(350, self.coord_y_for_table,
                                         text=f'{abs(round(100 * (1 - pi / (4 * self.count_probability)), 5))} %',
                                         font=('Comic Sans MS', 15), fill='#AFB9BA')

            self.coord_y_for_table += 45

    def stop_process(self, process):
        """
        Останавливает процесс при определённом условии
        (в данном случае при достижении общего кол-ва точек 3000)
        """
        if len(self.points.canvas_points_ids) == 20000:
            self.root.after_cancel(process)

    def clean_canvas(self, group: str):
        """
        Очистка элементов определённоой группы
        Args:
            group: список с дескрипторами удаляемой группы элементов
        """
        for canvas_obj in self._all_lists[group]:
            self.chart_canvas.delete(canvas_obj)
        self._all_lists[group] = []

    def run(self):
        self.root.mainloop()

    @property
    def count_probability(self):
        """
        Вероятностт попадания точки в круг
        Returns: вероятность попадания точки в круг
        """
        return len(self._all_lists['_caught_points']) / self.points.drawed_points


if __name__ == '__main__':
    app = App()
    app.run()
