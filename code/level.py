import pygame 
from settings import *
from tile import Tile
from player import Player
from debug import debug
from support import *
from random import choice, randint
from weapon import Weapon
from ui import UI
from enemy import Enemy
from particles import AnimationPlayer
from magic import MagicPlayer
from upgrade import Upgrade

BOSS_COL    = '392'
MINION_COLS = ('390','391','393')

class Level:
	def __init__(self):
		self.display_surface = pygame.display.get_surface()
		self.game_paused = False

		self.visible_sprites    = YSortCameraGroup()
		self.obstacle_sprites   = pygame.sprite.Group()
		self.current_attack     = None
		self.attack_sprites     = pygame.sprite.Group()
		self.attackable_sprites = pygame.sprite.Group()

		# phase: 1=kroco, 2=boss
		self.phase              = 1
		self.boss_data          = []
		self._phase2_triggered  = False

		self.create_map()

		self.ui      = UI()
		self.upgrade = Upgrade(self.player)

		self.animation_player = AnimationPlayer()
		self.magic_player     = MagicPlayer(self.animation_player)

		self.hud_font = pygame.font.Font(UI_FONT, 18)

	# ── MAP ──────────────────────────────────────────────────────
	def create_map(self):
		layouts = {
			'boundary': import_csv_layout('map/map_FloorBlocks.csv'),
			'grass':    import_csv_layout('map/map_Grass.csv'),
			'object':   import_csv_layout('map/map_Objects.csv'),
			'entities': import_csv_layout('map/map_Entities.csv'),
		}
		graphics = {
			'grass':   import_folder('graphics/Grass'),
			'objects': import_folder('graphics/objects'),
		}

		for style, layout in layouts.items():
			for ri, row in enumerate(layout):
				for ci, col in enumerate(row):
					if col == '-1': continue
					x, y = ci * TILESIZE, ri * TILESIZE

					if style == 'boundary':
						Tile((x,y), [self.obstacle_sprites], 'invisible')

					elif style == 'grass':
						Tile((x,y),
							[self.visible_sprites, self.obstacle_sprites, self.attackable_sprites],
							'grass', choice(graphics['grass']))

					elif style == 'object':
						Tile((x,y), [self.visible_sprites, self.obstacle_sprites],
							'object', graphics['objects'][int(col)])

					elif style == 'entities':
						if col == '394':
							self.player = Player(
								(x,y), [self.visible_sprites],
								self.obstacle_sprites,
								self.create_attack, self.destroy_attack,
								self.create_magic)
						elif col in MINION_COLS:
							name = {'390':'bamboo','391':'spirit'}.get(col,'squid')
							Enemy(name, (x,y),
								[self.visible_sprites, self.attackable_sprites],
								self.obstacle_sprites,
								self.damage_player,
								self.trigger_death_particles,
								self.add_exp)
						elif col == BOSS_COL:
							self.boss_data.append(('raccoon', (x,y)))

	# ── ATTACK / MAGIC ───────────────────────────────────────────
	def create_attack(self):
		self.current_attack = Weapon(self.player,
			[self.visible_sprites, self.attack_sprites])

	def create_magic(self, style, strength, cost):
		if style == 'heal':
			self.magic_player.heal(self.player, strength, cost, [self.visible_sprites])
		if style == 'flame':
			self.magic_player.flame(self.player, cost,
				[self.visible_sprites, self.attack_sprites])

	def destroy_attack(self):
		if self.current_attack:
			self.current_attack.kill()
		self.current_attack = None

	def player_attack_logic(self):
		for atk in self.attack_sprites:
			hits = pygame.sprite.spritecollide(atk, self.attackable_sprites, False)
			for t in hits:
				if t.sprite_type == 'grass':
					pos = t.rect.center
					off = pygame.math.Vector2(0, 75)
					for _ in range(randint(3,6)):
						self.animation_player.create_grass_particles(
							pos - off, [self.visible_sprites])
					t.kill()
				else:
					t.get_damage(self.player, atk.sprite_type)

	# ── DAMAGE PLAYER — ini yang diperbaiki ──────────────────────
	def damage_player(self, amount, attack_type):
		if self.player.vulnerable:
			self.player.health -= amount
			self.player.vulnerable = False
			self.player.hurt_time  = pygame.time.get_ticks()
			self.animation_player.create_particles(
				attack_type, self.player.rect.center, [self.visible_sprites])

			# Pastikan health tidak negatif
			if self.player.health <= 0:
				self.player.health = 0
				self.game_paused   = True   # freeze game saat mati

	def trigger_death_particles(self, pos, ptype):
		self.animation_player.create_particles(ptype, pos, self.visible_sprites)

	def add_exp(self, amount):
		self.player.exp += amount

	def toggle_menu(self):
		self.game_paused = not self.game_paused

	# ── ENEMY HELPERS ────────────────────────────────────────────
	def get_enemies(self):
		return [s for s in self.visible_sprites.sprites()
				if hasattr(s, 'sprite_type') and s.sprite_type == 'enemy']

	def spawn_bosses(self):
		for name, pos in self.boss_data:
			Enemy(name, pos,
				[self.visible_sprites, self.attackable_sprites],
				self.obstacle_sprites,
				self.damage_player,
				self.trigger_death_particles,
				self.add_exp)
		self.boss_data = []

	# ── CHECK GAME OVER — dipanggil dari main.py ─────────────────
	def check_game_over(self):
		"""Return 'win' / 'lose' / 'phase2' / None"""

		# Cek player mati — pakai health langsung, bukan flag
		if self.player.health <= 0:
			return 'lose'

		enemies = self.get_enemies()

		# Fase 1 selesai → semua kroco mati → spawn boss
		if self.phase == 1 and len(enemies) == 0 and not self._phase2_triggered:
			self._phase2_triggered = True
			self.phase             = 2
			self.game_paused       = False   # pastikan tidak freeze
			self.spawn_bosses()
			return 'phase2'

		# Fase 2 selesai → semua boss mati → menang
		if self.phase == 2 and len(enemies) == 0:
			return 'win'

		return None

	# ── HUD counter musuh ────────────────────────────────────────
	def draw_wave_hud(self):
		enemies = self.get_enemies()
		cnt     = len(enemies)
		if self.phase == 1:
			txt = f'FASE 1  |  Kroco tersisa: {cnt}'
			col = (220, 180, 50)
		else:
			txt = f'FASE 2  |  BOSS tersisa: {cnt}'
			col = (220, 80, 60)

		surf = self.hud_font.render(txt, True, col)
		rect = surf.get_rect(topright=(WIDTH - 20, 20))
		bg   = pygame.Surface((rect.width + 20, rect.height + 10))
		bg.set_alpha(160)
		bg.fill((10, 10, 10))
		self.display_surface.blit(bg,   (rect.x - 10, rect.y - 5))
		self.display_surface.blit(surf,  rect)

	# ── RUN ──────────────────────────────────────────────────────
	def run(self):
		self.visible_sprites.custom_draw(self.player)
		self.ui.display(self.player)
		self.draw_wave_hud()

		if self.game_paused:
			self.upgrade.display()
		else:
			self.visible_sprites.update()
			self.visible_sprites.enemy_update(self.player)
			self.player_attack_logic()


# ═════════════════════════════════════════════════════════════════
class YSortCameraGroup(pygame.sprite.Group):
	def __init__(self):
		super().__init__()
		self.display_surface = pygame.display.get_surface()
		self.half_width      = self.display_surface.get_size()[0] // 2
		self.half_height     = self.display_surface.get_size()[1] // 2
		self.offset          = pygame.math.Vector2()
		self.floor_surf      = pygame.image.load('graphics/tilemap/ground.png').convert()
		self.floor_rect      = self.floor_surf.get_rect(topleft=(0,0))

	def custom_draw(self, player):
		self.offset.x = player.rect.centerx - self.half_width
		self.offset.y = player.rect.centery - self.half_height
		fp = self.floor_rect.topleft - self.offset
		self.display_surface.blit(self.floor_surf, fp)
		for sprite in sorted(self.sprites(), key=lambda s: s.rect.centery):
			self.display_surface.blit(sprite.image, sprite.rect.topleft - self.offset)

	def enemy_update(self, player):
		for s in [x for x in self.sprites()
				  if hasattr(x, 'sprite_type') and x.sprite_type == 'enemy']:
			s.enemy_update(player)