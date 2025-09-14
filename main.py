from machine import Pin, PWM
from time import sleep, localtime
from lcd import LCD

# --- LCD setup ---
lcd = LCD(rs=1, en=9, d4=10, d5=11, d6=12, d7=14)

# --- Backlight ---
backlight = PWM(Pin(28))
backlight.freq(1000)

def set_backlight(level):
    backlight.duty_u16(level)

# --- Buttons ---
inc_btn = Pin(2, Pin.IN, Pin.PULL_UP)
dec_btn = Pin(3, Pin.IN, Pin.PULL_UP)
confirm_btn = Pin(4, Pin.IN, Pin.PULL_UP)

# --- Servo motor ---
servo = PWM(Pin(13))  # Single servo on GP13
servo.freq(50)

def set_servo(angle):
    min_us = 500
    max_us = 2500
    us = min_us + (max_us - min_us) * angle / 180
    duty = int(us * 65535 / 20000)
    servo.duty_u16(duty)

# --- Passive buzzer ---
buzzer = PWM(Pin(15))
buzzer.duty_u16(0)

def beep(freq=1000, duration=0.1, duty=32768):
    buzzer.freq(freq)
    buzzer.duty_u16(duty)
    sleep(duration)
    buzzer.duty_u16(0)

# --- Sounds ---
def inc_beep(): beep(1200, 0.08)
def dec_beep(): beep(1000, 0.08)
def confirm_beep(): beep(2000, 0.12)
def back_beep():
    for _ in range(2):
        beep(800, 0.15, 12000)
        sleep(0.25)
def armed_beep():
    for f in (1200, 1600, 2000):
        beep(f, 0.15)
        sleep(0.1)
def cancel_beep(): beep(600, 0.25, 16000)

# --- Variables ---
hour = 1
minute = 0
ampm = "AM"
stage = "greeting"
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# --- Helpers ---
def two_digit(n): return "{:02d}".format(n)

def servo_wiggle():
    for _ in range(2):
        set_servo(85)
        sleep(0.05)
        set_servo(95)
        sleep(0.05)

def backlight_blink():
    for duty in range(65535, 10000, -4000):
        set_backlight(duty)
        sleep(0.02)
    sleep(0.3)
    for duty in range(10000, 65535, 4000):
        set_backlight(duty)
        sleep(0.02)

def blink_message(msg, duration=0.8):
    lcd.clear()
    lcd.putstr(msg)
    backlight_blink()
    sleep(duration)

# --- Greeting screen ---
lcd.clear()
lcd.putstr("Hello User")
lcd.move_to(0, 1)
lcd.putstr("Press Enter...")
set_backlight(65535)

# --- Main loop ---
while True:

    if stage == "greeting":
        if confirm_btn.value() == 0:
            lcd.clear()
            lcd.putstr("Set Hour:")
            stage = "hour"
            sleep(0.3)

    elif stage == "hour":
        lcd.move_to(0, 1)
        lcd.putstr(two_digit(hour) + "   ")

        if inc_btn.value() == 0:
            hour = (hour + 1) % 13 or 1
            inc_beep()
            sleep(0.3)

        if dec_btn.value() == 0:
            hour = (hour - 1) % 13 or 12
            dec_beep()
            sleep(0.3)

        if confirm_btn.value() == 0:
            lcd.clear()
            lcd.putstr("Set Minute:")
            stage = "minute"
            confirm_beep()
            sleep(0.3)

    elif stage == "minute":
        lcd.move_to(0, 1)
        lcd.putstr(two_digit(minute) + "   ")

        if inc_btn.value() == 0:
            minute = (minute + 1) % 60
            inc_beep()
            sleep(0.3)

        if dec_btn.value() == 0:
            minute = (minute - 1) % 60
            dec_beep()
            sleep(0.3)

        if confirm_btn.value() == 0:
            lcd.clear()
            lcd.putstr("AM or PM?")
            stage = "ampm"
            confirm_beep()
            sleep(0.3)

    elif stage == "ampm":
        lcd.move_to(0, 1)
        lcd.putstr(ampm + "   ")

        if inc_btn.value() == 0 or dec_btn.value() == 0:
            ampm = "PM" if ampm == "AM" else "AM"
            confirm_beep()
            sleep(0.3)

        if confirm_btn.value() == 0:
            today_idx = localtime()[6]
            today_name = days[today_idx]
            lcd.clear()
            final_time = f"{two_digit(hour)}:{two_digit(minute)} {ampm}"
            lcd.putstr(final_time)
            lcd.move_to(0, 1)
            lcd.putstr(today_name)
            stage = "confirm_screen"
            confirm_beep()
            sleep(1.2)

    elif stage == "confirm_screen":
        lcd.clear()
        final_time = f"{two_digit(hour)}:{two_digit(minute)} {ampm}"
        today_name = days[localtime()[6]]
        lcd.putstr(final_time)
        lcd.move_to(0, 1)
        lcd.putstr(today_name)
        sleep(2)

        lcd.clear()
        lcd.putstr("Press=Enter")
        lcd.move_to(0, 1)
        lcd.putstr("Hold=Back")

        pressed = 0
        while True:
            if confirm_btn.value() == 0:
                sleep(0.1)
                pressed += 1
            else:
                if pressed >= 10:
                    back_beep()
                    lcd.clear()
                    lcd.putstr("Going Back")
                    sleep(1)
                    stage = "hour"
                    break
                elif pressed > 0:
                    armed_beep()
                    lcd.clear()
                    lcd.putstr("Alarm Armed")
                    sleep(1.5)
                    stage = "armed"
                    break
                pressed = 0

    elif stage == "armed":
        last_display = ""
        while stage == "armed":
            now = localtime()
            current_hour = now[3]
            current_minute = now[4]

            current_ampm = "AM"
            display_hour = current_hour
            if current_hour == 0:
                display_hour = 12
            elif current_hour >= 12:
                current_ampm = "PM"
                if current_hour > 12:
                    display_hour = current_hour - 12

            real_time = f"{two_digit(display_hour)}:{two_digit(current_minute)} {current_ampm}"
            set_time = f"{two_digit(hour)}:{two_digit(minute)} {ampm}"
            display_text = f"Now:{real_time}\nSet:{set_time}"

            if display_text != last_display:
                lcd.clear()
                lcd.putstr("Now:" + real_time)
                lcd.move_to(0, 1)
                lcd.putstr("Set:" + set_time)
                last_display = display_text

            pressed = 0
            if confirm_btn.value() == 0:
                while confirm_btn.value() == 0:
                    sleep(0.1)
                    pressed += 1
                if pressed >= 10:
                    cancel_beep()
                    blink_message("Alarm Canceled", duration=1.0)
                    servo_wiggle()
                    sleep(0.8)
                    blink_message("Ready", duration=1.0)
                    lcd.clear()
                    stage = "greeting"
                    break

            if (display_hour == hour and
                current_minute == minute and
                current_ampm == ampm):

                lcd.clear()
                lcd.putstr("Dispensing...")
                set_servo(180)
                beep(1500, 0.3)
                sleep(5)

                lcd.clear()
                lcd.putstr("Food Ready!")
                set_servo(0)
                sleep(2)

                stage = "greeting"
                break

            sleep(1)

