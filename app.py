from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import time
import threading

app = Flask(__name__)
socketio = SocketIO(app)

# 타이머 상태 관리 변수
timer_running = False
timer_paused = False
current_thread = None
remaining_time = 0  # 남은 시간 저장
original_time = 0   # 원래 입력한 시간 저장


# 타이머 카운트다운 함수
def countdown_timer():
    global timer_running, timer_paused, remaining_time
    while remaining_time > 0 and timer_running:
        if not timer_paused:  # 일시정지 상태가 아닐 때만 감소
            socketio.emit('update_timer', {'time': remaining_time})  # 클라이언트에 타이머 값 전송
            time.sleep(1)
            remaining_time -= 1
    if remaining_time == 0 and timer_running:
        socketio.emit('update_timer', {'time': "끝!"})  # 타이머 종료 메시지
    timer_running = False


@socketio.on('start_timer')
def handle_start_timer(data):
    global timer_running, current_thread, remaining_time, original_time
    if not timer_running:  # 처음 시작할 때
        timer_running = True
        remaining_time = int(data['duration'])  # 사용자가 입력한 시간 저장
        original_time = remaining_time  # 원래 시간 저장
        current_thread = threading.Thread(target=countdown_timer)
        current_thread.start()
    elif timer_paused:  # 일시정지 상태에서 다시 시작
        resume_timer()


@socketio.on('pause_timer')
def handle_pause_timer():
    global timer_paused
    timer_paused = not timer_paused  # 토글 (일시정지 <-> 다시 시작)


@socketio.on('reset_timer')
def handle_reset_timer():
    global timer_running, timer_paused, remaining_time
    timer_running = False
    timer_paused = False
    remaining_time = original_time  # 원래 입력했던 시간으로 복원
    socketio.emit('update_timer', {'time': remaining_time})  # 클라이언트에 원래 시간 전송


def resume_timer():
    global timer_paused, current_thread
    timer_paused = False
    current_thread = threading.Thread(target=countdown_timer)
    current_thread.start()


@app.route('/')
def home():
    return render_template('timer.html')


if __name__ == '__main__':
    socketio.run(app, debug=True)
