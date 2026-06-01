def draw_victory(self):
        self.draw_bg()
        self.overlay(110)
        cx,cy=W//2,H//2
        if self.ui_victory:
            rect=self.ui_victory.get_rect(center=(cx,cy))
            self.screen.blit(self.ui_victory,rect)
            self._win_btn=pygame.Rect(rect.centerx-92,rect.centery+150,200,48)
        else:
            shadow_text(self.screen,'VICTORY!',self.f72,GOLD,cx,cy-100)
            self._win_btn=pygame.Rect(cx-150,cy+60,180,68)
        draw_panel(self.screen,self._win_btn,(15,15,15),(40,200,40),8,2)
        shadow_text(self.screen,'BACK TO MENU',self.f14,WHITE,
                    self._win_btn.centerx,self._win_btn.centery)