"""Constants and configs"""
from bot import Keyboard


GREETING_MESSAGE = """Привет👋

Через меня вы будетe получать следующую полезную информацию:
📝Домашние задания
🕘Общие мероприятия (школьные концерты, сбор макулатуры и т.д.)
📆События в классе (даты экзаменов, контрольных, экскурсий и т.п)

Всё будет приходить прямо в этот чат

👇Нажмите кнопку \"Календарь\", чтобы увидеть, что запланировано на ближайшее будущее"
"""

LESSONS_SCHEDULE = """
<code><b>📌 Понедельник</b></code>
<code>1)</code> Химия
<code>2)</code> Алгебра
<code>3)</code> Английский язык (у своих учителей)
<code>4)</code> Информатика
<code>5)</code> Обществознание
<code>6)</code> Физкультура

<code><b>📌 Вторник</b></code>
<code>1)</code> Английский язык
    (у группы Браниновой - Лукина,
    у группы Лукиной - Рудь,
    у группы Рудь - Бранинова)
<code>2)</code> Геометрия
<code>3)</code> Русский
<code>4)</code> Электив по русскому/математике
<code>5)</code> История
<code>6)</code> ОБЖ

<code><b>📌 Среда</b></code>
<code>1)</code> Английский язык
    (у группы Браниновой - Рудь,
    у группы Рудь - Лукина,
    у группы Лукиной - Бранинова)
<code>2)</code> Электив по математике/русскому
<code>3)</code> Литература
<code>4)</code> Физика
<code>5)</code> История
<code>6)</code> Физкультура

<code><b>📌 Четверг</b></code>
<code>1)</code> Астрономия
<code>2)</code> Английский язык (у своих учителей)
<code>3)</code> Английский язык
    (у группы Рудь - Бранинова,
    у группы Браниновой - Лукина,
    у группы Лукины - Рудь)
<code>4)</code> Русский
<code>5)</code> Литература
<code>6)</code> География

<code><b>🍻 Пятница</b></code>
<code>1)</code> Английский язык (у группы Браниновой - Рудь,
    у группы Рудь - Лукина,
    у группы Лукиной - Бранинова)
<code>2)</code> Биология
<code>3)</code> История
<code>4)</code> Обществознание
<code>5)</code> Алгебра
<code>6)</code> Геометрия

<code><b>🍻 Суббота</b></code>
<code>1)</code> Литература
<code>2)</code> Физика
<code>3)</code> Электив по биологии/обществознанию
<code>4)</code> Физкультура
<code>5)</code> Алгебра
<code>6)</code> Электив по истории/литературе
"""

FOOD_CANTEEN_SCHEDULE = """
<code><b>1 неделя</b></code>
<code>🍑 Понедельник</code>: борщ без фасоли, плов, капуста, яблоко
<code>🍑 Вторник</code>: гороховый суп, пюре вкусное с рыбной котлетой, морковь, йогурт
<code>🍑 Среда</code>: овощной суп со свежей капустой, куриная котлета с масленными макаронами, винегрет, яблоко, оранжевый сок
<code>🍑 Четверг</code>: рассольник, ленивые голубцы, помидоры с луком, апельсин, компот
<code>🍻 Пятница</code>: суп с лапшой, курицей и картошкой, рыба гадкая с картошкой, огурцы маринованные с луком, йогурт, морс
<code>🍻 Суббота</code>: щи с перловкой, гречка с печенкой, свекла, яблоко, сок

<code><b>2 неделя</b></code>
<code>🍑 Понедельник</code>: овощной суп со свежей капустой, рис с куриной котлетой в сыре, оливье без соуса школьный, сок яблочный, яблоко
<code>🍑 Вторник</code>: рыбный суп, рагу, салат из капусты яблока и морковки, йогурт
<code>🍑 Среда</code>: борщ с фасолью, гречка с котлетой вкусной, булка с творогом, полпомидора
<code>🍑 Четверг</code>: рассольник, рыба в яйце с пюре, свекла, йогурт
<code>🍻 Пятница</code>: похлебка крестьянская, курица в сметанном соусе, морковка, яблоко
<code>🍻 Суббота</code>: суп с картошкой, тушеные овощи с куриной котлетой, маринованный огурец, яблочный сок, яблоко
"""

SUBJECTS_MENU = Keyboard(
    [
        ["Русский", "Литература"],
        ["Алгебра", "Геометрия"],
        ["Профильная математика"],
        ["Базовая математика"],
        ["Информатика (Марина Гарриевна)"],
        ["Информатика (Попова)"],
        ["История", "Биология"],
        ["Электив по истории"],
        ["Обществознание", "ОБЖ"],
        ["Электив по биологии"],
        ["Химия", "Физика"],
        ["Астрономия", "География"],
        ["Английский язык (группа Браниновой)"],
        ["Английский язык (группа Лукиной)"],
        ["Английский язык (группа Рудь)"],
        ["Физкультура"],
    ]
)
