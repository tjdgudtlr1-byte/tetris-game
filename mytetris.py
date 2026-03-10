import sys
import pygame 
import random

pygame.init() # pygame 내부 기능들을 사용할 준비를 하는것

#----- 상수 -----

background = pygame.display.set_mode((500, 560)) # 게임 창의 크기를 설정
pygame.display.set_caption("Tetris") # 게임 창의 제목을 설정

CELL_SIZE = 28 # 테트리스 블록의 셀 크기
COL = 10 # 테트리스 보드의 열 수
ROW = 20 # 테트리스 보드의 행 수
HEIGHT = CELL_SIZE * ROW # 게임 창의 높이
WIDTH = CELL_SIZE * COL # 게임 창의 너비
FIELD = [[0 for _ in range(COL)] for _ in range(ROW)] # 게임 보드를 2차원 리스트로 초기화
FONT = pygame.font.SysFont("malgungothic", 30, True, False) # 폰트 설정 
TEXT = FONT.render("SCORE", True, (255, 255, 255), None) # SCORE 텍스트 렌더링
FPS = 60
score = 0 # 점수 초기화
current_type = 'O' # 컬러 설정 초기값 
rotation = 0

#-----색상 정의-----

BLOCK_COLOR = {
    'I': (255, 216, 216), # 살구색
    'O': (255, 0, 127),   # 핫핑크  
    'T': (128, 0, 128),   # 보라색
    'S': (0, 255, 0),     # 초록색
    'Z': (255, 0, 0),     # 빨간색
    'J': (0, 0, 255),     # 파란색
    'L': (255, 165, 0)    # 주황색
}

#-----블록 모양 정의----- 

SHAPES = {
    'I': [
         [
         [1, 1, 1, 1] #rotation 0
         ],
         
         [
         [1],
         [1],
         [1],
         [1],
         ], #rotation 1
    ],
    
    'O': [
        [
        [1, 1], #rotation 0
        [1, 1]
        ],
    ],

    'T' : [
        [
        [0, 1, 0], #rotation 0
        [1, 1, 1]
        ],

        [
        [1, 0], #rotation 1
        [1, 1],
        [1, 0]
        ],

        [
        [1, 1, 1], #rotation 2
        [0, 1, 0]
        ],

        [
        [0, 1], #rotation 3
        [1, 1],
        [0, 1]
        ],
    ],

    'S' : [
        [
        [0, 1, 1], #rotation 0
        [1, 1, 0]
        ],

        [
        [1, 0], #rotation 1
        [1, 1],
        [0, 1]
        ],
    ],

    'Z' : [
        [
        [1, 1, 0], #rotation 0
        [0, 1, 1]
        ],

        [
        [0, 1], #rotation 1
        [1, 1],
        [1, 0]
        ],
    ],

    'J' : [
        [
        [0, 0, 1],  #rotation 0
        [1, 1, 1]
        ],

        [
        [1, 0],  #rotation 1
        [1, 0],
        [1, 1]
        ],

        [
        [1, 1, 1], #rotation 2
        [1, 0, 0]
        ],

        [
        [1, 1],  #rotation 3
        [0, 1],
        [0, 1]
        ],
    ],

    'L' : [
        [
        [1, 0, 0], #rotation 0
        [1, 1, 1]
        ],

        [
        [1, 1], #rotation 1
        [1, 0],
        [1, 0]
        ],

        [ 
        [1, 1, 1], #rotation 2
        [0, 0, 1]
        ],

        [
        [0, 1], #rotation 3
        [0, 1],
        [1, 1]
        ],
    ]
}


block = SHAPES ['O'][0]
block_x = 4
block_y = 0

#-----게임 루프-----

def main():
    global block_x, block_y, block, rotation, score

    while True:
        for event in pygame.event.get(): # for문을 작동시켜서 pygame에서 발생하는 event가 있다면 그것을 get해서 가져오고 그 event가 무엇이지 하나하나 for문으로 검색해보는데 현재 발생한 event타입이 종료시키는 명령이라면 현재 돌아가는 while문의 조건을 false로 바꾼다. 
            if event.type == pygame.QUIT: # 게임 창을 닫는 이벤트가 발생하면
                pygame.quit() # pygame을 종료
                sys.exit() # 시스템을 종료

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if not check_collision(offset_x=-1):
                        block_x -= 1
                elif event.key == pygame.K_RIGHT:
                    if not check_collision(offset_x=1):
                        block_x += 1
                elif event.key == pygame.K_DOWN:
                    if not check_collision(offset_y=1):
                        block_y += 1

                elif event.key == pygame.K_UP:
                    if not check_collision(offset_x=1, offset_y=1):
                        rotation = (rotation + 1) % len(SHAPES[current_type])
                        block = SHAPES[current_type][rotation]

        background.fill((0,0,0)) # 게임 창의 배경을 검은색으로 채움 이게 다른것들보다 위에있어야.. 아래것들이 보여

        draw_grid() 
        draw_score()
        draw_block()
        drop_block()
        draw_field()
        
        cleared = clear_line()

        if cleared > 0:
            score += cleared * 100
            #print(f"SCORE : {score}") 테스트완료
        
        if check_collision():
            block_y = float(int(block_y)) #소수점 버리고 정수 위치로
            while check_collision(): #정수로 맞춰도 충돌상태면 한칸위로 
                block_y -= 1 # 한마디로 블록 머리끄댕이잡고 올려버림ㅋㅋㅋ
            fix_block()
        else:
            drop_block()

        pygame.display.flip() # 게임 창을 업데이트하여 변경 사항을 반영
        pygame.time.Clock().tick(FPS) # 게임 루프의 실행 속도를 FPS로 제한
        
#-----Piece-----

def draw_field():
    for y in range(ROW):
        for x in range(COL):
            if FIELD[y][x] == 1:
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)

                color = BLOCK_COLOR[current_type]
                pygame.draw.rect(background, color, rect)
                pygame.draw.rect(background, (255, 255, 255), rect, 1)

#-----Board-----

def draw_grid(): # 격자 그리기 함수를 draw_grid()라고 호출하면 격자 그리는 코드 실행됨
    for y in range(ROW):     # for문을 이용해서 행 반복 0~19 20행 격자 좌표임
        for x in range(COL):  # for 문을 이용하여 열 반복 0~9 10열

            rect = pygame.Rect(  #사각형의 위치와 크기를 정의한다. Rect(x, y, width, height) 형식으로 사용됨
                x * CELL_SIZE, # CELL_SIZE는 30이므로 x = 3 y = 5 따라서 3 * 30,
                y * CELL_SIZE, # 5 * 30,
                CELL_SIZE, # 30,
                CELL_SIZE # 30
            ) #즉 Rect(90, 150, 30, 30)위치가 (90, 150)인 사각형이 만들어진다 이게 바로 격자 한칸

            pygame.draw.rect(background, (255,255,255), rect, 1) #어디에 그릴지, 색, 어떤 사각형, 두께 정의 화면에 흰색으로 사각형을 테두리 두께 1로 그려라

def draw_score(): # 점수 그리기 함수 draw_score()라고 호출하면 점수 그리는 코드 실행됨
    background.blit(FONT.render(f"SCORE: {score}", True, (255, 255, 255), None), (325, 20))

def draw_block(): # 롯청기가 바닥을 훑듯이 칸 하나하나 확인하게 만들어보자
    for y in range(len(block)): #첫 번쨰 줄부터 확인하자 (위에서 아래로 내려가는줄)
        for x in range(len(block[y])): #그 줄의 왼쪽 칸부터 오른쪽 칸까지 하나씩 살펴보자 ( 왼쪽에서 오른쪽으로 가는 칸)
            if block[y][x] == 1: #만약 그 칸이 0이면 지나가고 1이면 블록을 그려야해 판단하는 조건문
                rect = pygame.Rect((block_x + x) * CELL_SIZE, (block_y + y) * CELL_SIZE, CELL_SIZE, CELL_SIZE) #블록의 위치와 크기를 정의하는 사각형을 만들어보자
            
                color = BLOCK_COLOR[current_type]
                pygame.draw.rect(background, color, rect) #이거 (0, 255, 255)로 고정시키면 내가 의도한 색이아니기때문에, BLOCK_COLOR 딕셔너리에서 'O'블록의 색상을 가져온겨 ㅋ
                pygame.draw.rect(background, (255, 255, 255), rect, 1)  # 이건 도형에 격자 그리기라 그냥 냅둬도됨  

#---- 게임 ----

def drop_block():
    global block_y
    block_y += 0.03 # 블록이 떨어지는 속도 조절

def check_collision(offset_x=0, offset_y=0): # 충돌 체크 함수
    global block_y, block_x, block, FIELD # 전역 변수
    for y in range(len(block)):
        for x in range(len(block[y])):
            #if block[y][x]: 수정전
            if block[y][x] == 1:
                next_x = block_x + x + offset_x
                next_y = int(block_y) + y + offset_y

                if next_x < 0 or next_x >= COL or next_y >= ROW:
                    return True
                
                if FIELD[next_y][next_x] == 1:
                    return True
    return False
                #수정전 if next_y >= 0 and FIELD[next_y][next_x] == 1:
                #   return True
    
                #if int(block_y) + y + 1 >= len(FIELD):
                #    return True
                #if FIELD[int(block_y)+y+1][block_x + x]:
                #    return True
    #return False

def fix_block(): # 블록 고정 함수
    global block_x, block_y, block, FIELD, current_type, rotation # 나중에는 이거 class로묶어서... 해결할 수 있다면..ㅋ

    for y in range(len(block)):
        for x in range(len(block[y])):
            if block[y][x] == 1:
                FIELD[int(block_y) + y][block_x + x] = 1
    rotation = 0            
    current_type = random.choice(list(SHAPES.keys()))
    block = SHAPES[current_type][0]

    block_x = 4
    block_y = 0

def clear_line(): # 값이 1인 FIELD를 삭제하는 함수
    global FIELD

    new_field = [row for row in FIELD if 0 in row] # 꽉 차지 않은(0이 하나라도 있는) 줄만 골라서 새 리스트 만듬

    line_cleared = ROW - len(new_field) #지워진 줄 수 계산
    
    for _ in range(line_cleared): #삭제된 만큼 맨 위에 빈 줄을 추가해
        new_field.insert(0, [0 for _ in range(COL)])

        FIELD = new_field # 업데이트 된 지도를 진짜 FIELD에 덮어씌움
    
    return line_cleared #결과 보고
      
# 이파일을 직접 실행했을 때만 main()을 실행하시오
if __name__ == "__main__":
    main()
