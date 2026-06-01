import pygame, sys, math
from settings import *
from level import Level

W, H = WIDTH, HEIGTH

# ── Palette ──────────────────────────────────────────────────────
GOLD   = (220,170, 50)
ORANGE = (220,120, 20)
DARK   = ( 18, 12,  6)
PANEL  = ( 28, 20, 10)
BORDER = (160,120, 40)
GREEN2 = (100,180, 70)
WHITE  = (238,238,238)
RED    = (200, 50, 40)
GREY   = (130,130,130)
BLACK  = (  0,  0,  0)

def draw_panel(surf, rect, fill=PANEL, border=BORDER, radius=12, bw=3):
    pygame.draw.rect(surf, fill,   rect, border_radius=radius)
    pygame.draw.rect(surf, border, rect, bw, border_radius=radius)

def shadow_text(surf, text, font, color, cx, cy, shadow=BLACK):
    s = font.render(text, True, shadow)
    m = font.render(text, True, color)
    surf.blit(s, s.get_rect(center=(cx+2, cy+2)))
    surf.blit(m, m.get_rect(center=(cx,   cy)))

def leaf_branch_pygame(surf, cx, cy, width=400):
    pygame.draw.line(surf,(80,50,20),(cx-width//2,cy),(cx+width//2,cy),4)
    for dx in range(-width//2, width//2+1, 35):
        lx = cx+dx
        ly = cy + (abs(dx)//50 - 3)
        pygame.draw.ellipse(surf,(55,110,35),(lx-8,ly-5,16,10))
        pygame.draw.ellipse(surf,(80,160,50),(lx-5,ly-8,10,10))

def corner_ornament(surf, x, y, flip_x=False, flip_y=False):
    sx = -1 if flip_x else 1
    sy = -1 if flip_y else 1
    pygame.draw.line(surf, GOLD, (x,y),(x+sx*18,y), 2)
    pygame.draw.line(surf, GOLD, (x,y),(x,y+sy*18), 2)
    pygame.draw.circle(surf, GOLD, (x,y), 3)


# ═══════════════════════════════════════════════════════════════
#  NAV BUTTON HELPER
#  Gambar tombol ← BACK dan NEXT → dengan style game
# ═══════════════════════════════════════════════════════════════
def draw_nav_buttons(surf, f18, f14, cx, by,
                     show_back=True, show_next=True,
                     back_label='◀  BACK', next_label='NEXT  ▶',
                     page_cur=None, page_total=None):
    """
    Gambar tombol navigasi di bawah dialog.
    Return: (rect_back, rect_next)  — rect bisa None kalau tidak ditampilkan
    """
    BTN_W, BTN_H = 140, 36
    GAP           = 30
    mouse         = pygame.mouse.get_pos()

    # posisi tombol
    back_rect = pygame.Rect(cx - BTN_W - GAP//2, by, BTN_W, BTN_H)
    next_rect = pygame.Rect(cx + GAP//2,          by, BTN_W, BTN_H)

    # ── BACK button ────────────────────────────────────────────
    if show_back:
        hover_b = back_rect.collidepoint(mouse)
        fill_b  = (55, 35, 12) if hover_b else (35, 22,  8)
        brd_b   = (200,150, 50) if hover_b else BORDER
        draw_panel(surf, back_rect, fill_b, brd_b, 10, 2)
        # ikon panah kiri lebih besar
        arrow_x = back_rect.x + 22
        arrow_y = back_rect.centery
        pygame.draw.polygon(surf, GOLD,
            [(arrow_x,     arrow_y),
             (arrow_x+14,  arrow_y-9),
             (arrow_x+14,  arrow_y+9)])
        lbl = f14.render(back_label, True, WHITE if not hover_b else GOLD)
        surf.blit(lbl, lbl.get_rect(midleft=(arrow_x+22, back_rect.centery)))
        # garis dekorasi atas-bawah
        pygame.draw.line(surf, (100,80,30),
            (back_rect.x+8, back_rect.y+4),
            (back_rect.right-8, back_rect.y+4), 1)
        pygame.draw.line(surf, (100,80,30),
            (back_rect.x+8, back_rect.bottom-4),
            (back_rect.right-8, back_rect.bottom-4), 1)
    else:
        back_rect = None

    # ── NEXT button ────────────────────────────────────────────
    if show_next:
        hover_n = next_rect.collidepoint(mouse)
        fill_n  = (20, 55, 18) if hover_n else (14, 38, 12)
        brd_n   = (100,200, 60) if hover_n else (60,140,35)
        draw_panel(surf, next_rect, fill_n, brd_n, 10, 2)
        lbl = f14.render(next_label, True, WHITE if not hover_n else (160,255,100))
        surf.blit(lbl, lbl.get_rect(midright=(next_rect.right-22, next_rect.centery)))
        # ikon panah kanan
        arrow_x = next_rect.right - 22
        arrow_y = next_rect.centery
        pygame.draw.polygon(surf, (120,220,60),
            [(arrow_x,     arrow_y),
             (arrow_x-14,  arrow_y-9),
             (arrow_x-14,  arrow_y+9)])
        pygame.draw.line(surf, (60,120,30),
            (next_rect.x+8, next_rect.y+4),
            (next_rect.right-8, next_rect.y+4), 1)
        pygame.draw.line(surf, (60,120,30),
            (next_rect.x+8, next_rect.bottom-4),
            (next_rect.right-8, next_rect.bottom-4), 1)
    else:
        next_rect = None

    # ── Page indicator ─────────────────────────────────────────
    if page_cur is not None and page_total is not None:
        for i in range(page_total):
            dot_x = cx - (page_total-1)*12 + i*24
            dot_y = by + BTN_H + 16
            col   = GOLD if i == page_cur else (80,65,30)
            pygame.draw.circle(surf, col, (dot_x, dot_y), 6)
            pygame.draw.circle(surf, (50,40,15), (dot_x, dot_y), 6, 1)

    return back_rect, next_rect


# ═══════════════════════════════════════════════════════════════
#  GAME CLASS
# ═══════════════════════════════════════════════════════════════
class Game:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()

        self.screen = pygame.display.set_mode((W,H))
        pygame.display.set_caption('Forest of Fate')
        self.clock  = pygame.time.Clock()
        self.tick   = 0

        # joystick
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
        self._pad_cd = 0

        # BGM
        self.bgm        = pygame.mixer.Sound('audio/main.ogg')
        self.win_sound  = pygame.mixer.Sound('audio/winsound.mp3')
        self.gameover_sound = pygame.mixer.Sound('audio/gameover.WAV')
        self.click_sound= pygame.mixer.Sound('audio/dropmcbaru.WAV')
        self.click_sound.set_volume(1.0)
        self.bgm.set_volume(0.2)
        self.bgm.play(loops=-1)

        # fonts
        self.f72 = pygame.font.Font(UI_FONT, 72)
        self.f52 = pygame.font.Font(UI_FONT, 52)
        self.f36 = pygame.font.Font(UI_FONT, 36)
        self.f26 = pygame.font.Font(UI_FONT, 26)
        self.f22 = pygame.font.Font(UI_FONT, 22)
        self.f18 = pygame.font.Font(UI_FONT, 18)
        self.f14 = pygame.font.Font(UI_FONT, 14)
        self.f12 = pygame.font.Font(UI_FONT, 12)

        # load UI images
        def load_ui(name, size=None):
            try:
                img = pygame.image.load(f'graphics/{name}').convert_alpha()
                if size: img = pygame.transform.smoothscale(img, size)
                return img
            except:
                return None

        self.img_dialog       = load_ui('ui_dialog_panel.png', size=(1000,220))
        self.img_portrait     = load_ui('ui_portrait.png')
        self.img_start_bg     = load_ui('ui_start_overlay.jpg', size=(W,H)) or load_ui('ui_start_overlay.png', size=(W,H))
        self.img_howtoplay_bg = load_ui('ui_howtoplay.jpg', size=(860,538)) or load_ui('ui_howtoplay.png', size=(860,538))
        self.ui_gameover      = load_ui('ui_gameover.png',size=(660,338))
        self.ui_victory       = load_ui('ui_victory.png',size=(560,300))

        self.level = Level()
        self.state = 'start'

        # transisi pixel
        self.trans_mode           = None
        self.next_state_target    = None
        self.pixel_size           = 20
        self.grid_cols            = W // self.pixel_size
        self.grid_rows            = H // self.pixel_size
        self.trans_grid_cells     = [(c,r) for c in range(self.grid_cols)
                                           for r in range(self.grid_rows)]
        self.pixel_index_progress = 0
        self.pixel_speed          = 180
        self.trans_delay_timer    = 0

        # story
        self.story_pages = [
            "Halo!\nKamu berada di Hutan Fate, hutan ini dulunya damai,\nnamun sekarang dipenuhi oleh monster dan kegelapan.\nTugasmu adalah mengembalikan kedamaian dan energi alam.",
            "Hutan ini telah dicemari oleh kroco-kroco kelam.\nMakhluk kecil ini berkeliaran dan mengganggu\nkeseimbangan alam. Bersihkan semuanya\ndan pulihkan ketenangan hutan.",
            "Di dalam hutan terdapat sumber kegelapan yang sangat kuat.\nKalahkan boss besar yang bersembunyi di sudut hutan.\nHanya dengan mengalahkan mereka, energi alam dapat\ndipulihkan dan Hutan Fate kembali damai.",
        ]
        self.story_idx = 0

        # phase intro — sekarang juga punya sub-pages
        self.phase_intro_pages = [
            [
                ("FASE 1 : BERSIHKAN HUTAN",
                 "Hutan ini telah dicemari oleh kroco-kroco kelam.\nBersihkan semuanya dan pulihkan ketenangan hutan."),
                ("",
                 "Ada 4 jenis musuh: Squid, Raccoon, Spirit, dan Bamboo.\nKalahkan semua musuh yang ada di peta!"),
            ],
            [
                ("FASE 2 : KALAHKAN DUA BOS",
                 "Sekarang, boss besar menunggu di sudut hutan.\nKalahkan mereka dan pulihkan energi alam yang hilang."),
                ("FASE 2 : TIPS MELAWAN BOS",
                 "Gunakan sihir (CTRL) untuk damage lebih besar.\nJangan lupa upgrade statsmu dengan menekan M!"),
            ],
        ]
        self.phase_idx     = 0   # fase ke-0 atau ke-1
        self.phase_sub_idx = 0   # sub-page dalam satu fase

        # simpan rect nav button agar bisa dicek klik
        self._nav_back = None
        self._nav_next = None

    # ── helpers ────────────────────────────────────────────────
    def draw_bg(self):
        self.screen.fill((71,170,136))
        self.level.visible_sprites.custom_draw(self.level.player)

    def overlay(self, alpha=160):
        ov = pygame.Surface((W,H), pygame.SRCALPHA)
        ov.fill((0,0,0,alpha))
        self.screen.blit(ov,(0,0))

    def title_panel(self, text, cx, cy, pw=520):
        r = pygame.Rect(cx-pw//2, cy-26, pw, 52)
        draw_panel(self.screen, r, (45,28,10), GOLD, 8, 2)
        leaf_branch_pygame(self.screen, cx, cy-26, pw-20)
        leaf_branch_pygame(self.screen, cx, cy+26, pw-20)
        shadow_text(self.screen, text, self.f26, GOLD, cx, cy)

    # ── 1. START ───────────────────────────────────────────────
    def draw_start(self):
        self.tick += 1
        cx = W//2
        if self.img_start_bg:
            self.screen.blit(self.img_start_bg,(0,0))
        else:
            self.draw_bg(); self.overlay(90)
            shadow_text(self.screen,'FOREST OF',self.f52,(60,140,30),cx,155)
            shadow_text(self.screen,'FATE',self.f72,ORANGE,cx,245)
        if (self.tick//28)%2==0:
            bw2,bh2=380,46
            br=pygame.Rect(cx-bw2//2,H//2+150,bw2,bh2)
            draw_panel(self.screen,br,(10,10,10),(200,200,200),8,2)
            parts=[('PRESS ',(238,238,238)),('SPACE',GOLD),('  TO PLAY',(238,238,238))]
            total_w=sum(self.f18.size(p)[0] for p,_ in parts)
            xx=cx-total_w//2
            for txt,col in parts:
                s=self.f18.render(txt,True,col)
                self.screen.blit(s,(xx,H//2+164)); xx+=s.get_width()
        hint=self.f12.render('or CLICK anywhere',True,(150,150,150))
        self.screen.blit(hint,hint.get_rect(center=(cx,H//2+220)))

    # ── TRANSISI ───────────────────────────────────────────────
    def start_transition_to(self, target_state):
        import random
        self.state='transition'; self.next_state_target=target_state
        self.pixel_index_progress=0; self.trans_delay_timer=0
        self.trans_mode='fade_out'
        random.shuffle(self.trans_grid_cells)

    def draw_transition(self):
        import random
        if self.trans_mode=='fade_out':
            self.draw_start()
            self.pixel_index_progress+=self.pixel_speed
            if self.pixel_index_progress>=len(self.trans_grid_cells):
                self.pixel_index_progress=len(self.trans_grid_cells)
                self.trans_mode='hold_delay'
        elif self.trans_mode=='hold_delay':
            self.screen.fill((15,15,15))
            self.trans_delay_timer+=1
            if self.trans_delay_timer>=40:
                self.state=self.next_state_target
                self.trans_mode='fade_in'
                random.shuffle(self.trans_grid_cells)
        elif self.trans_mode=='fade_in':
            self.draw_howtoplay()
            self.pixel_index_progress-=self.pixel_speed
            if self.pixel_index_progress<=0:
                self.pixel_index_progress=0; self.trans_mode=None
        if self.trans_mode=='hold_delay':
            self.screen.fill((15,15,15))
        elif self.trans_mode in('fade_out','fade_in'):
            for i in range(int(self.pixel_index_progress)):
                if i<len(self.trans_grid_cells):
                    col,row=self.trans_grid_cells[i]
                    pygame.draw.rect(self.screen,(15,15,15),
                        (col*self.pixel_size,row*self.pixel_size,
                         self.pixel_size,self.pixel_size))

    # ── 2. HOW TO PLAY ─────────────────────────────────────────
    def draw_howtoplay(self):
        self.draw_bg(); self.overlay(175)
        if self.img_howtoplay_bg:
            img_w,img_h=self.img_howtoplay_bg.get_size()
            px,py=(W-img_w)//2,(H-img_h)//2
            self.screen.blit(self.img_howtoplay_bg,(px,py))
            obw=int(325*(img_w/1000)); obh=int(52*(img_h/625))
            obx=(W//2)-(obw//2); oby=py+int(538*(img_h/625))
            self._htp_btn=pygame.Rect(obx,oby,obw,obh)
        else:
            cx=W//2; px,py,pw,ph=130,40,1020,640
            panel=pygame.Rect(px,py,pw,ph)
            draw_panel(self.screen,panel,(22,15,7),BORDER,14,4)
            self.title_panel('HOW TO PLAY',cx,py+44,pw-60)
            obx,oby,obw,obh=cx-145,py+ph-70,290,50
            obr=pygame.Rect(obx,oby,obw,obh)
            draw_panel(self.screen,obr,(28,55,18),(80,160,40),10,3)
            shadow_text(self.screen,'◆  OKAYY!  ◆',self.f22,GOLD,cx,oby+25)
            self._htp_btn=obr

    # ══════════════════════════════════════════════════════════
    # 3. STORY — dengan UI tombol BACK & NEXT
    # ══════════════════════════════════════════════════════════
    def draw_story(self):
        self.draw_bg(); self.overlay(155)
        self.tick += 1
        cx   = W//2
        dpx  = 60
        dpy  = H - 270

        # panel dialog
        if self.img_dialog:
            self.screen.blit(self.img_dialog,(115,450))

        # teks isi
        tx,ty_ = dpx+330, dpy+55
        lines = self.story_pages[self.story_idx].split('\n')
        for i,line in enumerate(lines):
            ls = self.f14.render(line,True,WHITE)
            self.screen.blit(ls,(tx, ty_+i*26))

        # ── tombol BACK & NEXT ─────────────────────────────────
        btn_y     = dpy + 170          # posisi Y tombol (dalam panel dialog)
        show_back = self.story_idx > 0
        is_last   = self.story_idx >= len(self.story_pages)-1
        next_lbl  = 'MULAI  ▶' if is_last else 'NEXT  ▶'

        self._nav_back, self._nav_next = draw_nav_buttons(
            self.screen, self.f18, self.f14,
            cx, btn_y,
            show_back=show_back,
            show_next=True,
            back_label='◀  BACK',
            next_label=next_lbl,
            page_cur=self.story_idx,
            page_total=len(self.story_pages)
        )

        # hint keyboard kecil
        hint = self.f12.render('← Backspace = Back  |  Space / Enter = Next',True,(130,110,60))
        self.screen.blit(hint, hint.get_rect(center=(cx, dpy+240)))

    # ══════════════════════════════════════════════════════════
    # 4. PHASE INTRO — dengan UI tombol BACK & NEXT + sub-page
    # ══════════════════════════════════════════════════════════
    def draw_phase_intro(self):
        self.draw_bg(); self.overlay(155)
        self.tick += 1
        cx  = W//2
        dpx = 60
        dpy = H - 270

        # panel dialog
        if self.img_dialog:
            self.screen.blit(self.img_dialog,(115,450))

        sub_pages  = self.phase_intro_pages[self.phase_idx]
        ptitle, pdesc = sub_pages[self.phase_sub_idx]
        tx = dpx + 350

        # judul fase
        pt_shadow = self.f18.render(ptitle,True,BLACK)
        pt_s      = self.f18.render(ptitle,True,GOLD)
        self.screen.blit(pt_shadow,(tx+2, dpy+57))
        self.screen.blit(pt_s,     (tx,   dpy+55))

        # deskripsi
        lines = pdesc.split('\n')
        for i,line in enumerate(lines):
            ls = self.f14.render(line,True,WHITE)
            self.screen.blit(ls,(tx, dpy+90+i*26))

        # ── tombol BACK & NEXT ─────────────────────────────────
        btn_y     = dpy + 175
        total_sub = len(sub_pages)

        # back: bisa kembali ke sub-page sebelumnya
        # (kalau sub_idx==0 dan phase_idx==1 bisa kembali ke story)
        show_back = (self.phase_sub_idx > 0) or (self.phase_idx > 0)
        is_last   = self.phase_sub_idx >= total_sub - 1
        next_lbl  = 'MAIN!  ▶' if is_last else 'NEXT  ▶'

        self._nav_back, self._nav_next = draw_nav_buttons(
            self.screen, self.f18, self.f14,
            cx, btn_y,
            show_back=show_back,
            show_next=True,
            back_label='◀  BACK',
            next_label=next_lbl,
            page_cur=self.phase_sub_idx,
            page_total=total_sub
        )

        # label fase kecil di pojok kanan atas panel
        fase_lbl = self.f12.render(f'Fase {self.phase_idx+1}  •  {self.phase_sub_idx+1}/{total_sub}',
                                   True,(150,130,80))
        self.screen.blit(fase_lbl,(dpx+990, dpy+255))

        hint = self.f12.render('← Backspace = Back  |  Space / Enter = Next',True,(130,110,60))
        self.screen.blit(hint, hint.get_rect(center=(cx, dpy+240)))

    # ── LOGIC NAVIGASI STORY ───────────────────────────────────
    def story_next(self):
        self.story_idx += 1
        if self.story_idx >= len(self.story_pages):
            self.phase_idx     = 0
            self.phase_sub_idx = 0
            self.state         = 'phase_intro'

    def story_back(self):
        if self.story_idx > 0:
            self.story_idx -= 1

    # ── LOGIC NAVIGASI PHASE INTRO ─────────────────────────────
    def phase_next(self):
        sub_pages = self.phase_intro_pages[self.phase_idx]
        if self.phase_sub_idx < len(sub_pages)-1:
            # masih ada sub-page berikutnya
            self.phase_sub_idx += 1
        else:
            # sub-page habis → mulai main
            self.state = 'playing'

    def phase_back(self):
        if self.phase_sub_idx > 0:
            # kembali ke sub-page sebelumnya di fase ini
            self.phase_sub_idx -= 1
        elif self.phase_idx > 0:
            # kembali ke fase sebelumnya, sub-page terakhir
            self.phase_idx    -= 1
            self.phase_sub_idx = len(self.phase_intro_pages[self.phase_idx])-1
        else:
            # kembali ke story halaman terakhir
            self.story_idx = len(self.story_pages)-1
            self.state     = 'story'

    # ── 5. GAME OVER ───────────────────────────────────────────
    def draw_gameover(self):
        self.draw_bg(); self.overlay(130)
        cx,cy=W//2,H//2-80
        if self.ui_gameover:
            rect=self.ui_gameover.get_rect(center=(cx,cy))
            self.screen.blit(self.ui_gameover,rect)
            self._lose_btn=pygame.Rect(rect.centerx-92,rect.centery+150,200,48)
        else:
            shadow_text(self.screen,'GAME OVER',self.f72,RED,cx,cy-100)
            self._lose_btn=pygame.Rect(cx-150,cy+60,180,68)
        draw_panel(self.screen,self._lose_btn,(40,15,15),(100,40,40),8,2)
        shadow_text(self.screen,'BACK TO MENU',self.f14,WHITE,
                    self._lose_btn.centerx,self._lose_btn.centery)

    # ── 6. VICTORY ─────────────────────────────────────────────
    def draw_victory(self):
        self.draw_bg()
        self.overlay(110)
        cx,cy=W//2,H//2
        if self.ui_victory:
            rect=self.ui_victory.get_rect(center=(cx,cy-80))
            self.screen.blit(self.ui_victory,rect)
            self._win_btn=pygame.Rect(rect.centerx-92,rect.centery+80,200,48)
        else:
            shadow_text(self.screen,'VICTORY!',self.f72,GOLD,cx,cy-100)
            self._win_btn=pygame.Rect(cx-150,cy+60,180,68)
        draw_panel(self.screen,self._win_btn,(15,15,15),(40,200,40),8,2)
        shadow_text(self.screen,'BACK TO MENU',self.f14,WHITE,
                    self._win_btn.centerx,self._win_btn.centery)
    # ── GAMEPAD ────────────────────────────────────────────────
    def pad_confirm(self):
        if not self.joystick: return False
        now=pygame.time.get_ticks()
        if now-self._pad_cd<280: return False
        try:
            if self.joystick.get_button(0) or self.joystick.get_button(7):
                self._pad_cd=now; 
                return True
        except: pass
        return False

    def pad_back(self):
        if not self.joystick:
            return False

        now = pygame.time.get_ticks()

        if now - self._pad_cd < 280:
            return False

        try:
            # tombol B pada Xbox Controller
            if self.joystick.get_button(1):
                self._pad_cd = now
                return True
        except:
            pass

        return False

    # ── RESET ──────────────────────────────────────────────────
    def reset_game(self):
        self.win_sound.stop(); self.bgm.stop(); pygame.mixer.stop()
        self.bgm.play(loops=-1)
        self.level         = Level()
        self.story_idx     = 0
        self.phase_idx     = 0
        self.phase_sub_idx = 0
        self.state         = 'start'

    # ══════════════════════════════════════════════════════════
    # MAIN LOOP
    # ══════════════════════════════════════════════════════════
    def run(self):
        while True:
            confirm = False
            go_back = False
            mouse_click_pos = None

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

                if event.type == pygame.KEYDOWN:
                    # confirm
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        self.click_sound.play(); confirm = True
                    # back
                    if event.key in (pygame.K_BACKSPACE, pygame.K_LEFT):
                        self.click_sound.play();
                        go_back = True
                    # toggle upgrade menu
                    if event.key == pygame.K_m and self.state == 'playing':
                        self.level.toggle_menu()
                    # shortcut debug win
                    if event.key == pygame.K_z:
                        pygame.mixer.stop(); self.win_sound.play()
                        self.state = 'win'

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_click_pos = event.pos
                    self.click_sound.play()

                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button in (0,7):

                        if self.state in ('start','how_to_play','story','phase_intro','win','lose'):
                            self.click_sound.play(); 
                            confirm = True

            if self.pad_confirm(): 
                confirm = True

            if self.pad_back():
                if self.state != 'playing':
                    self.click_sound.play()
                    go_back = True

            # ── cek klik tombol nav ──────────────────────────────
            if mouse_click_pos:
                mp = mouse_click_pos
                if self.state in ('story','phase_intro'):
                    if self._nav_next and self._nav_next.collidepoint(mp):
                        confirm = True
                    if self._nav_back and self._nav_back.collidepoint(mp):
                        go_back = True

            # ── state machine ────────────────────────────────────
            if self.state == 'transition':
                self.draw_transition()

            elif self.state == 'start':
                self.draw_start()
                if confirm or mouse_click_pos:
                    self.start_transition_to('how_to_play')

            elif self.state == 'how_to_play':
                self.draw_howtoplay()
                if confirm:
                    self.state='story'; self.story_idx=0
                if mouse_click_pos and hasattr(self,'_htp_btn'):
                    if self._htp_btn.collidepoint(mouse_click_pos):
                        self.state='story'; self.story_idx=0

            elif self.state == 'story':
                self.draw_story()
                if confirm:   self.story_next()
                if go_back:   self.story_back()

            elif self.state == 'phase_intro':
                self.draw_phase_intro()
                if confirm:   self.phase_next()
                if go_back:   self.phase_back()

            elif self.state == 'playing':
                self.screen.fill(WATER_COLOR)
                self.level.run()
                res = self.level.check_game_over()
                if res == 'win':
                    pygame.mixer.stop(); self.win_sound.play(); self.state='win'
                elif res == 'lose':
                    pygame.mixer.stop(); 
                    self.gameover_sound.play();
                    self.state = 'lose'
                elif res == 'phase2':
                    self.phase_idx=1; self.phase_sub_idx=0; self.state='phase_intro'

            elif self.state == 'win':
                self.draw_victory()
                if confirm or (mouse_click_pos and hasattr(self,'_win_btn')
                               and self._win_btn.collidepoint(mouse_click_pos)):
                    self.reset_game()

            elif self.state == 'lose':
                self.draw_gameover()
                if confirm or (mouse_click_pos and hasattr(self,'_lose_btn')
                               and self._lose_btn.collidepoint(mouse_click_pos)):
                    self.reset_game()

            pygame.display.update()
            self.clock.tick(FPS)


if __name__ == '__main__':
    game = Game()
    game.run()