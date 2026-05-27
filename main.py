import streamlit as st
import streamlit.components.v1 as components

# 페이지 기본 설정
st.set_page_config(page_title="당곡고 FPS 훈련장", page_icon="🎯", layout="centered")

st.markdown("""
    <h1 style='text-align: center; color: #ff4b4b;'>🔫 1인칭 FPS 에임 트레이닝</h1>
    <p style='text-align: center;'>과녁을 조준하고 마우스 좌클릭으로 사격하세요! 제한 시간 30초!</p>
""", unsafe_allow_html=True)

# 1인칭 FPS 게임을 완벽하게 구현하기 위한 HTML/CSS/JS 코드
fps_game_code = """
<!DOCTYPE html>
<html>
<head>
<style>
    body {
        margin: 0;
        padding: 0;
        font-family: 'Arial', sans-serif;
        user-select: none; /* 드래그 방지 */
    }

    /* 상단 UI (점수 및 타이머) */
    #ui-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 20px;
        background-color: #1a1c23;
        color: white;
        border-radius: 10px 10px 0 0;
    }

    .status { font-size: 22px; font-weight: bold; }
    
    #start-btn {
        background-color: #ff4655; /* 발로란트 레드 */
        color: white;
        border: none;
        padding: 10px 25px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 5px;
        cursor: pointer;
        transition: 0.2s;
    }
    #start-btn:hover { background-color: #d43743; }
    #start-btn:disabled { background-color: #555; cursor: not-allowed; }

    /* 게임 화면 (훈련장 배경) */
    #game-area {
        width: 100%;
        height: 500px;
        /* 훈련장 느낌의 배경색 */
        background: radial-gradient(circle at 50% 50%, #3a3f47 0%, #17181d 100%);
        position: relative;
        overflow: hidden;
        border-radius: 0 0 10px 10px;
        
        /* 💚 커스텀 초록색 십자선(크로스헤어) 설정 */
        cursor: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32"><line x1="16" y1="4" x2="16" y2="12" stroke="%2300ff00" stroke-width="2"/><line x1="16" y1="20" x2="16" y2="28" stroke="%2300ff00" stroke-width="2"/><line x1="4" y1="16" x2="12" y2="16" stroke="%2300ff00" stroke-width="2"/><line x1="20" y1="16" x2="28" y2="16" stroke="%2300ff00" stroke-width="2"/><circle cx="16" cy="16" r="2" fill="%2300ff00"/></svg>') 16 16, crosshair;
        box-shadow: 0 5px 15px rgba(0,0,0,0.5);
    }

    /* 🔴 과녁 (타겟) */
    #target {
        width: 45px;
        height: 45px;
        background-color: #ff4655; /* 발로란트 레드 */
        border: 3px solid white;
        border-radius: 50%;
        position: absolute;
        display: none;
        box-shadow: 0 0 15px rgba(255, 70, 85, 0.6);
        z-index: 10;
        transition: background-color 0.05s; /* 피격 시 흰색으로 변하는 효과용 */
    }

    /* 🔫 1인칭 총기 위치 (마우스 시선 이동 적용 컨테이너) */
    #gun-wrapper {
        position: absolute;
        bottom: -20px;
        right: 15%;
        width: 200px;
        height: 300px;
        pointer-events: none; /* 중요! 총이 클릭을 방해하지 않게 함 */
        z-index: 20;
        transition: transform 0.1s ease-out; /* 시선 이동 부드럽게 */
    }

    /* 사격 반동을 위한 컨테이너 */
    #gun-recoil-box {
        width: 100%;
        height: 100%;
        position: relative;
        transform-origin: bottom center;
    }

    /* CSS로 그린 총기 디자인 */
    .gun-body {
        position: absolute;
        bottom: 0;
        right: 20px;
        width: 80px;
        height: 250px;
        background: linear-gradient(to right, #2a2a2a, #1a1a1a);
        border-radius: 10px 10px 0 0;
        box-shadow: -10px 0 20px rgba(0,0,0,0.6);
        border-left: 2px solid #555;
    }
    .gun-barrel {
        position: absolute;
        bottom: 250px;
        right: 35px;
        width: 40px;
        height: 120px;
        background: linear-gradient(to right, #111, #222);
        border-radius: 5px 5px 0 0;
    }
    
    /* 🔥 총구 화염 (Muzzle Flash) */
    #muzzle-flash {
        position: absolute;
        bottom: 360px;
        right: -10px;
        width: 130px;
        height: 130px;
        background: radial-gradient(circle, #ffeb3b 20%, #ff9800 50%, transparent 70%);
        border-radius: 50%;
        opacity: 0; /* 평소엔 안 보임 */
        pointer-events: none;
    }

    /* 💥 사격 애니메이션 (반동) */
    .fire-recoil {
        animation: recoil-anim 0.15s ease-out;
    }
    @keyframes recoil-anim {
        0% { transform: translateY(0) rotate(0deg); }
        30% { transform: translateY(40px) rotate(8deg); } /* 뒤로 밀림 */
        100% { transform: translateY(0) rotate(0deg); }
    }

    /* 💥 총구 화염 애니메이션 */
    .fire-flash {
        animation: flash-anim 0.1s ease-out;
    }
    @keyframes flash-anim {
        0% { opacity: 0; transform: scale(0.5); }
        50% { opacity: 1; transform: scale(1.2); }
        100% { opacity: 0; transform: scale(1); }
    }
</style>
</head>
<body>

    <!-- UI 영역 -->
    <div id="ui-bar">
        <div class="status">🎯 명중: <span id="score">0</span></div>
        <button id="start-btn">훈련 시작 🚀</button>
        <div class="status">⏳ 남은 시간: <span id="time">30</span>초</div>
    </div>

    <!-- 게임 화면 -->
    <div id="game-area">
        <div id="target"></div>
        
        <!-- 1인칭 총기 모델 -->
        <div id="gun-wrapper">
            <div id="gun-recoil-box">
                <div class="gun-body"></div>
                <div class="gun-barrel"></div>
                <div id="muzzle-flash"></div>
            </div>
        </div>
    </div>

    <script>
        const gameArea = document.getElementById('game-area');
        const target = document.getElementById('target');
        const scoreDisplay = document.getElementById('score');
        const timeDisplay = document.getElementById('time');
        const startBtn = document.getElementById('start-btn');
        
        const gunWrapper = document.getElementById('gun-wrapper');
        const gunRecoilBox = document.getElementById('gun-recoil-box');
        const muzzleFlash = document.getElementById('muzzle-flash');

        let score = 0;
        let timeLeft = 30;
        let timerId = null;
        let isPlaying = false;

        // 1. 과녁을 랜덤 위치로 이동
        function moveTarget() {
            // 과녁의 크기(45px)를 고려하여 밖으로 나가지 않게 계산
            const maxX = gameArea.clientWidth - 50; 
            const maxY = gameArea.clientHeight - 50;
            
            const randomX = Math.floor(Math.random() * maxX) + 5;
            const randomY = Math.floor(Math.random() * maxY) + 5;
            
            target.style.left = randomX + 'px';
            target.style.top = randomY + 'px';
        }

        // 2. 사격 효과 (반동 및 총구 화염) - 배경을 클릭하든 과녁을 클릭하든 무조건 발생
        gameArea.addEventListener('mousedown', (e) => {
            if(!isPlaying) return;

            // 기존 애니메이션 초기화 (연타 시 뚝뚝 끊기지 않도록 리셋)
            gunRecoilBox.classList.remove('fire-recoil');
            muzzleFlash.classList.remove('fire-flash');
            
            // 브라우저 렌더링 강제 업데이트 (Reflow)
            void gunRecoilBox.offsetWidth; 
            
            // 애니메이션 다시 적용
            gunRecoilBox.classList.add('fire-recoil');
            muzzleFlash.classList.add('fire-flash');
        });

        // 3. 과녁 명중 처리
        target.addEventListener('mousedown', (e) => {
            if(!isPlaying) return;
            score++;
            scoreDisplay.textContent = score;

            // 명중 시 찰나의 순간 하얀색으로 번쩍이는 효과(Hit Feedback)
            target.style.backgroundColor = 'white';
            
            setTimeout(() => {
                target.style.backgroundColor = '#ff4655'; // 원래 색으로 복구
                moveTarget(); // 새로운 위치로 이동
            }, 40); // 0.04초 딜레이 후 이동
            
            // 이벤트 전파를 막지 않음으로써 부모(gameArea)의 사격 효과(반동)도 함께 일어나게 함
        });

        // 4. 마우스 시선 이동 처리 (FPS Sway 효과)
        gameArea.addEventListener('mousemove', (e) => {
            if(!isPlaying) return;
            
            const rect = gameArea.getBoundingClientRect();
            // 화면 중심부 계산
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            // 현재 마우스 위치와 화면 중심의 거리 계산
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            // 마우스가 이동한 방향으로 총기를 살짝(0.04배율) 움직여줌
            const offsetX = (x - centerX) * 0.04;
            const offsetY = (y - centerY) * 0.04;

            gunWrapper.style.transform = `translate(${offsetX}px, ${offsetY}px)`;
        });

        // 5. 게임 시작 로직
        function startGame() {
            score = 0;
            timeLeft = 30;
            scoreDisplay.textContent = score;
            timeDisplay.textContent = timeLeft;
            isPlaying = true;
            
            target.style.display = 'block';
            startBtn.disabled = true;
            
            moveTarget();

            timerId = setInterval(() => {
                timeLeft--;
                timeDisplay.textContent = timeLeft;
                
                if (timeLeft <= 0) {
                    endGame();
                }
            }, 1000);
        }

        // 6. 게임 종료 로직
        function endGame() {
            clearInterval(timerId);
            isPlaying = false;
            target.style.display = 'none';
            startBtn.disabled = false;
            
            // 총기 위치 중앙으로 초기화
            gunWrapper.style.transform = `translate(0px, 0px)`;
            
            alert('훈련 종료! 당신의 최종 명중 횟수는 ' + score + '회 입니다! 🎯');
        }

        startBtn.addEventListener('click', startGame);
    </script>
</body>
</html>
"""

# HTML을 Streamlit에 적용 (화면 높이를 600px로 넉넉하게 설정)
components.html(fps_game_code, height=600)

st.info("💡 **조작 팁:** 제한 시간 안에 최대한 빠르게 과녁(🔴)을 맞추세요. 클릭 시 발생하는 총의 반동(Recoil) 애니메이션과 마우스 방향으로 시선이 따라가는(Sway) 효과를 느껴보세요!")
