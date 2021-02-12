from tkinter import Tk, Canvas
from random import randint
from math import pi


class CanvasTemplate:
    font = 'Comic Sans MS', 15

    def __init__(self, width, height, bg='#2B2B2B', fg='#AFB9BA'):
        self.canvas = Canvas(width=width, height=height, bg=bg)
        self.width = width
        self.height = height
        self.bg = bg
        self.fg = fg
        self.canvas_ids = {}
        self.draw()

    def delete_group(self, group_name):
        for canvas_id in self.canvas_ids.get(group_name, []):
            self.canvas.delete(canvas_id)
        self.canvas_ids[group_name] = []
        self.canvas.delete(group_name)

    def clear(self):
        for group_name in self.canvas_ids:
            self.delete_group(group_name)
        self.canvas.delete('for clear')

    def convert_canvas_to_decart(self, coords):
        return coords[0] + self.center[0], self.center[1] - coords[1]

    def draw(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    @property
    def center(self):
        return self.width / 2, self.height / 2


class Chart(CanvasTemplate):
    pi_line_color = '#499C54'
    upper_text_color = '#648658'

    chart_line_opts = {
        'fill': '#4096C1',
        'width': 4
    }

    error = 1
    amount = 0
    amount_in = 0
    calc_pi = 0

    chart_line = None

    def __init__(self, width, height):
        super().__init__(width, height)
        self.chart_step = width / 10

    def __draw_pi_line(self):
        """
        Отрисовка линии, которая соответствует точному значению числа pi.
        """
        self.delete_group('pi line')
        self.canvas_ids['pi line'] = [self.canvas.create_line(0, self.center[1],
                                                              self.width, self.center[1],
                                                              fill=self.pi_line_color,
                                                              tags=('pi line',))]

    def __draw_upper_text(self):
        self.delete_group('upper text')

        self.canvas_ids['upper text'].append(self.canvas.create_text(
            self.center[0], self.height / 5, text=f'Истинное 𝝅 = {pi}',
            fill=self.upper_text_color, tags=('upper text',), font=self.font
        ))
        self.canvas_ids['upper text'].append(self.canvas.create_text(
            self.center[0], self.height / 5 + self.font[1], text=f'Погрешность = {self.error}%',
            fill=self.upper_text_color, tags=('upper text',), font=self.font
        ))

    def __draw_footer_text(self):
        self.delete_group('footer text')

        self.canvas_ids['footer text'].append(self.canvas.create_text(
            self.center[0], self.height * 4 / 5, text=f'Общее количество точек: {self.amount}',
            fill=self.fg, tags=('footer text',), font=self.font
        ))
        self.canvas_ids['footer text'].append(self.canvas.create_text(
            self.center[0], self.height * 4 / 5 - self.font[1], text=f'Точки в круге: {self.amount_in}',
            fill=self.fg, tags=('footer text',), font=self.font
        ))

    def __draw_chart(self):
        self.canvas.delete(self.chart_line)
        self.chart_line = self.canvas.create_line(0, 0, 0, 0, **self.chart_line_opts)

    def __update_chart_line(self):
        self.canvas.coords(self.chart_line, *self.__get_chart_line_coords(self.canvas.coords(self.chart_line)))

    def __get_chart_line_coords(self, old_coords):
        if old_coords[-2] + self.chart_step > self.width * 9 / 10:
            self.__scale_chart()
            self.chart_step /= 2

        old_coords.append(old_coords[-2] + self.chart_step)
        old_coords.append(self.center[1] - (self.height / (2 * pi)) * self.calc_pi)

        return old_coords

    def __scale_chart(self):
        self.canvas.coords(self.chart_line, *(coord / 2 if no % 2 == 0 else coord
                                              for no, coord in enumerate(self.canvas.coords(self.chart_line))))

    def draw(self):
        self.__draw_pi_line()
        self.__draw_upper_text()
        self.__draw_footer_text()

    def update(self):
        self.__draw_footer_text()
        self.__draw_upper_text()


class Tab(CanvasTemplate):
    columns = 'Кол-во точек', 'Число pi', 'Погрешность'

    data = []

    def __draw_grid(self):
        self.delete_group('grid')

        for width in range(0, self.width, self.column_width):
            line = self.canvas.create_line((width, 0), (width, self.height),
                                           fill=self.fg, tags=('grid',))
            self.canvas_ids['grid'].append(line)

        for height in range(0, self.height, self.column_height):
            line = self.canvas.create_line((self.width, height), (self.width, height),
                                           fill=self.fg, tags=('grid',))
            self.canvas_ids['grid'].append(line)

    def __draw_header(self):
        self.delete_group('header')

        self.canvas_ids['header'] = [
            self.canvas.create_text(self.column_width * no + self.column_width / 2, self.column_height / 2,
                                    text=cell, font=self.font, fill=self.fg)
            for no, cell in enumerate(self.columns)]

    def insert_data(self, data):
        data = list(data)
        if len(data) != len(self.columns):
            raise IndexError('data len must be equal to number of columns')

        row = len(self.canvas_ids['data']) // len(self.columns)
        self.canvas_ids['data'] += [
            self.canvas.create_text(self.column_width * no + self.column_width / 2,
                                    self.column_height * row + self.column_height / 2,
                                    text=str(cell), fill=self.fg, tags=('data',), font=self.font)
            for no, cell in enumerate(data)
        ]

    def draw(self):
        self.__draw_grid()
        self.__draw_header()

    def update(self):
        pass

    @property
    def column_height(self):
        return self.font[1] * 2

    @property
    def column_width(self):
        return int(self.width / len(self.columns))


class Quarter(CanvasTemplate):
    quarter_options = {
        'start': 0,
        'extent': -90,
        'width': 2,
        'outline': 'gray',
        'fill': '#3C3F41',
        'tags': ('quarter',)
    }

    points_options = {
        'radius': 3,
        'width': 0,
    }

    points_fill = '#ECBB06'
    points_in_quarter_fill = '#4096C1'

    points_limit = 500
    points_per_step = 10

    amount_of_points = 0
    amount_of_points_in = 0

    def __draw_quarter(self):
        self.delete_group('quarter')

        self.canvas_ids['quarter'] = [self.canvas.create_arc(0, 0, self.width, self.height, **self.quarter_options)]

    def __draw_point(self, xy, radius, **options):
        x, y = xy
        self.canvas_ids['points'].append(self.canvas.create_rectangle(x - radius, y - radius, x + radius, y + radius,
                                                                      tags=('points',), **options))
        if len(self.canvas_ids['points']) > self.points_limit:
            self.canvas.delete(self.canvas_ids['points'].pop(0))

    def __point_in_quarter(self, xy):
        x, y = xy
        return True if x ** 2 + y ** 2 <= self.width else False

    def draw_points(self):
        for point_no in range(self.points_per_step):
            xy = randint(0, self.width), randint(0, self.height)
            if self.__point_in_quarter(xy):
                fill = self.points_in_quarter_fill
                self.amount_of_points_in += 1
            else:
                fill = self.points_fill
            self.__draw_point(xy, fill=fill, **self.points_options)
            self.amount_of_points += 1

    def draw(self):
        self.__draw_quarter()
        self.draw_points()

    def update(self):
        self.draw_points()


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
