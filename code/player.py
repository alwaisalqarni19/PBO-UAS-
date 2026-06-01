import pygame 
from settings import *
from support import import_folder
from entity import Entity

DEADZONE = 0.3   # analog stick deadzone

class Player(Entity):
    def __init__(self,pos,groups,obstacle_sprites,create_attack,destroy_attack,create_magic):
        super().__init__(groups)
        self.image = pygame.image.load('graphics/test/player.png').convert_alpha()
        self.rect  = self.image.get_rect(topleft=pos)
        self.hitbox= self.rect.inflate(-6,HITBOX_OFFSET['player'])

        self.import_player_assets()
        self.status = 'down'

        # movement
        self.attacking = False
        self.attack_cooldown = 400
        self.attack_time = None
        self.obstacle_sprites = obstacle_sprites

        # weapon
        self.create_attack  = create_attack
        self.destroy_attack = destroy_attack
        self.weapon_index   = 0
        self.weapon         = list(weapon_data.keys())[self.weapon_index]
        self.can_switch_weapon   = True
        self.weapon_switch_time  = None
        self.switch_duration_cooldown = 200

        # magic
        self.create_magic      = create_magic
        self.magic_index       = 0
        self.magic             = list(magic_data.keys())[self.magic_index]
        self.can_switch_magic  = True
        self.magic_switch_time = None

        # stats
        self.stats      = {'health':100,'energy':60,'attack':10,'magic':4,'speed':5}
        self.max_stats  = {'health':300,'energy':140,'attack':20,'magic':10,'speed':10}
        self.upgrade_cost={'health':100,'energy':100,'attack':100,'magic':100,'speed':100}
        self.health = self.stats['health']
        self.energy = self.stats['energy'] * 0.8
        self.exp    = 0
        self.speed  = self.stats['speed']

        # damage timer
        self.vulnerable = True
        self.hurt_time  = None
        self.invulnerability_duration = 500

        # sound
        self.weapon_attack_sound = pygame.mixer.Sound('audio/sword.wav')
        self.weapon_attack_sound.set_volume(0.4)

        # ── Gamepad setup ────────────────────────────────────────
        pygame.joystick.init()
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

        # button held-state to avoid repeat (gamepad)
        self._pad_attack_held  = False
        self._pad_magic_held   = False
        self._pad_sw_held      = False
        self._pad_sm_held      = False
        self._pad_menu_held    = False

    def import_player_assets(self):
        path = 'graphics/player/'
        self.animations = {
            'up':[],'down':[],'left':[],'right':[],
            'right_idle':[],'left_idle':[],'up_idle':[],'down_idle':[],
            'right_attack':[],'left_attack':[],'up_attack':[],'down_attack':[]
        }
        for anim in self.animations:
            self.animations[anim] = import_folder(path + anim)

    # ── pad helper ───────────────────────────────────────────────
    def _pad_btn(self, btn):
        if not self.joystick: return False
        try: return self.joystick.get_button(btn)
        except: return False

    def _pad_axis(self, axis):
        if not self.joystick: return 0.0
        try: return self.joystick.get_axis(axis)
        except: return 0.0

    def _pad_hat(self):
        if not self.joystick: return (0,0)
        try: return self.joystick.get_hat(0)
        except: return (0,0)

    # ── INPUT ────────────────────────────────────────────────────
    def input(self):
        if self.attacking:
            return

        keys = pygame.key.get_pressed()

        # ── MOVEMENT : keyboard ──────────────────────────────────
        dx = dy = 0

        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx = -1; self.status = 'left'
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx =  1; self.status = 'right'
        if keys[pygame.K_UP]    or keys[pygame.K_w]: dy = -1; self.status = 'up'
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: dy =  1; self.status = 'down'

        # ── MOVEMENT : gamepad left stick + d-pad ────────────────
        ax = self._pad_axis(0)
        ay = self._pad_axis(1)
        hx, hy = self._pad_hat()

        if abs(ax) > DEADZONE:
            dx = ax
            self.status = 'right' if ax > 0 else 'left'
        if abs(ay) > DEADZONE:
            dy = ay
            self.status = 'down' if ay > 0 else 'up'
        if hx != 0:
            dx = hx
            self.status = 'right' if hx > 0 else 'left'
        if hy != 0:
            dy = -hy
            self.status = 'down' if hy < 0 else 'up'

        self.direction.x = dx
        self.direction.y = dy

        # ── ATTACK : SPACE or gamepad A (btn 0) ──────────────────
        pad_attack = self._pad_btn(0)
        if keys[pygame.K_SPACE] or (pad_attack and not self._pad_attack_held):
            self.attacking = True
            self.attack_time = pygame.time.get_ticks()
            self.create_attack()
            self.weapon_attack_sound.play()
        self._pad_attack_held = pad_attack

        # ── MAGIC : LCTRL or gamepad B (btn 1) ───────────────────
        pad_magic = self._pad_btn(1)
        if keys[pygame.K_LCTRL] or (pad_magic and not self._pad_magic_held):
            self.attacking = True
            self.attack_time = pygame.time.get_ticks()
            style    = list(magic_data.keys())[self.magic_index]
            strength = list(magic_data.values())[self.magic_index]['strength'] + self.stats['magic']
            cost     = list(magic_data.values())[self.magic_index]['cost']
            self.create_magic(style, strength, cost)
        self._pad_magic_held = pad_magic

        # ── SWITCH WEAPON : Q or gamepad LB (btn 4) ──────────────
        pad_sw = self._pad_btn(4)
        if (keys[pygame.K_q] or (pad_sw and not self._pad_sw_held)) and self.can_switch_weapon:
            self.can_switch_weapon  = False
            self.weapon_switch_time = pygame.time.get_ticks()
            self.weapon_index = (self.weapon_index + 1) % len(weapon_data)
            self.weapon = list(weapon_data.keys())[self.weapon_index]
        self._pad_sw_held = pad_sw

        # ── SWITCH MAGIC : E or gamepad RB (btn 5) ───────────────
        pad_sm = self._pad_btn(5)
        if (keys[pygame.K_e] or (pad_sm and not self._pad_sm_held)) and self.can_switch_magic:
            self.can_switch_magic  = False
            self.magic_switch_time = pygame.time.get_ticks()
            self.magic_index = (self.magic_index + 1) % len(magic_data)
            self.magic = list(magic_data.keys())[self.magic_index]
        self._pad_sm_held = pad_sm

    def get_status(self):
        if self.direction.x == 0 and self.direction.y == 0:
            if 'idle' not in self.status and 'attack' not in self.status:
                self.status += '_idle'

        if self.attacking:
            self.direction.x = 0
            self.direction.y = 0
            if 'attack' not in self.status:
                if 'idle' in self.status:
                    self.status = self.status.replace('_idle','_attack')
                else:
                    self.status += '_attack'
        else:
            if 'attack' in self.status:
                self.status = self.status.replace('_attack','')

    def cooldowns(self):
        now = pygame.time.get_ticks()
        if self.attacking:
            if now - self.attack_time >= self.attack_cooldown + weapon_data[self.weapon]['cooldown']:
                self.attacking = False
                self.destroy_attack()
        if not self.can_switch_weapon:
            if now - self.weapon_switch_time >= self.switch_duration_cooldown:
                self.can_switch_weapon = True
        if not self.can_switch_magic:
            if now - self.magic_switch_time >= self.switch_duration_cooldown:
                self.can_switch_magic = True
        if not self.vulnerable:
            if now - self.hurt_time >= self.invulnerability_duration:
                self.vulnerable = True

    def animate(self):
        anim = self.animations[self.status]
        self.frame_index += self.animation_speed
        if self.frame_index >= len(anim):
            self.frame_index = 0
        self.image = anim[int(self.frame_index)]
        self.rect  = self.image.get_rect(center=self.hitbox.center)
        if not self.vulnerable:
            self.image.set_alpha(self.wave_value())
        else:
            self.image.set_alpha(255)

    def get_full_weapon_damage(self):
        return self.stats['attack'] + weapon_data[self.weapon]['damage']

    def get_full_magic_damage(self):
        return self.stats['magic'] + magic_data[self.magic]['strength']

    def get_value_by_index(self,index):
        return list(self.stats.values())[index]

    def get_cost_by_index(self,index):
        return list(self.upgrade_cost.values())[index]

    def energy_recovery(self):
        if self.energy < self.stats['energy']:
            self.energy += 0.01 * self.stats['magic']
        else:
            self.energy = self.stats['energy']

    def update(self):
        self.input()
        self.cooldowns()
        self.get_status()
        self.animate()
        self.move(self.stats['speed'])
        self.energy_recovery()
