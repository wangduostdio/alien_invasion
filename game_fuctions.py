import sys
from time import sleep

import pygame
from bullet import Bullet
from alien import Alien

def read_file(stats):
	'''读取'''
	with open('high_score.txt') as file_object:
		contents = int(file_object.read())
		stats.high_score = contents

def write_file(stats):
	with open ('high_score.txt','w') as file_object:
		file_object.write(str(stats.high_score))

def check_keydown_events(event,ai_settings,screen,ship,bullets):
	'''响应按键'''
	if event.key == pygame.K_RIGHT:
		#向右移动飞船
		ship.moving_right = True
	elif event.key == pygame.K_LEFT:
		#向左移动飞船
		ship.moving_left = True	
	elif event.key == pygame.K_SPACE:
		fire_bullet(ai_settings,screen,ship,bullets)
	elif event.key == pygame.K_q:
		write_file(stats)
		sys.exit()

def check_keyup_events(event,ship):
	'''响应松开'''
	if event.key == pygame.K_RIGHT:
		ship.moving_right = False
	if event.key == pygame.K_LEFT:
		ship.moving_left = False		

def check_events(ai_settings,screen,stats,sb,play_button,ship,aliens,bullets):
	#响应键盘和鼠标事件
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			write_file(stats)
			sys.exit()
		elif event.type == pygame.KEYDOWN:
			check_keydown_events(event,ai_settings,screen,ship,bullets)
		elif event.type == pygame.KEYUP:
			check_keyup_events(event,ship)
		elif event.type == pygame.MOUSEBUTTONDOWN:
			mouse_x,mouse_y = pygame.mouse.get_pos()
			check_play_button(ai_settings,screen,stats,sb,play_button,
				ship,aliens,bullets,mouse_x,mouse_y)

def check_play_button(ai_settings,screen,stats,sb,play_button,ship,aliens,bullets,mouse_x,mouse_y):
	'''在点击PLAY时开始游戏'''
	button_clicked = play_button.rect.collidepoint(mouse_x,mouse_y)
	if button_clicked and not stats.game_active:
		#重置游戏设置
		ai_settings.initialize_dynamic_settings()

		#隐藏光标
		pygame.mouse.set_visible(False)

		#重制游戏统计信息
		stats.reset_stats()
		stats.game_active = True

		#重制计分牌图像
		sb.prep_score()
		sb.prep_high_score()
		sb.prep_level()
		sb.prep_ships()

		#清空外星人列表和子弹列表
		aliens.empty()
		bullets.empty()

		#创建一群新的外星人，并让飞船居中
		create_fleet(ai_settings,screen,ship,aliens)
		ship.center_ship()

def updated_screen(ai_settings,screen,stats,sb,ship,aliens,bullets,play_button):
	#更新屏幕上的图像且切换至新屏幕
	#每次循环重绘屏幕
	screen.fill(ai_settings.bg_color)

	#在飞船和外星人后面重绘所有子弹
	for bullet in bullets.sprites():
		bullet.draw_bullet()
	ship.blitme()
	aliens.draw(screen)

	#显示得分
	sb.show_score()

	#如果游戏处于非活动状态，则绘制PLAY按钮
	if not stats.game_active:
		play_button.draw_button()

	#让最近绘制的屏幕可见
	pygame.display.flip()

def update_bullets(ai_settings,screen,stats,sb,ship,aliens,bullets):
	'''更新子弹位置，并删除消失的子弹'''
	#更新子弹位置
	bullets.update()

	#删除已消失的子弹
	for bullet in bullets.copy():
		if bullet.rect.bottom <= 0:
			bullets.remove(bullet)
	check_bullet_alien_collisions(ai_settings,screen,stats,sb,ship,aliens,bullets)
	
def check_bullet_alien_collisions(ai_settings,screen,stats,sb,ship,aliens,bullets):
	#检查是否有子弹击中外星人
	#如果是这样，则删除相应的子弹和外星人
	collisions = pygame.sprite.groupcollide(bullets,aliens,True,True)

	if collisions:
		for aliens in collisions.values():
			stats.score += ai_settings.alien_points * len(aliens)
			sb.prep_score()
		check_high_score(stats,sb)

	if len(aliens) == 0:
		#删除现有的子弹,提高等级并新建一群外星人
		bullets.empty()
		ai_settings.increase_speed()

		#提高等级
		stats.level += 1
		sb.prep_level()

		create_fleet(ai_settings,screen,ship,aliens)


def fire_bullet(ai_settings,screen,ship,bullets):
	'''如果没有达到限制，就发射一颗子弹'''
	#创建新子弹，并将其加入到编组bullets中
	if len(bullets) < ai_settings.bullets_allowed:
		new_bullet = Bullet(ai_settings,screen,ship)
		bullets.add(new_bullet)

def get_number_aliens_x(ai_settings,alien_width):
	'''计算每行可容纳多少外星人群'''
	available_space_x = ai_settings.screen_width - 2 * alien_width
	print(ai_settings.screen_width)
	print(alien_width)
	numbers_alien_x = int(available_space_x / (2 * alien_width))
	return numbers_alien_x	

def get_number_rows(ai_settings,ship_height,alien_height):
	'''计算每列可容纳多少行外星人'''
	available_space_y = (ai_settings.screen_height - 3 * alien_height - ship_height)
	numbers_rows = int(available_space_y / (2 * alien_height))
	return numbers_rows

def create_alien(ai_settings,screen,aliens,alien_number,row_number):
	'''创建一个外星人并加入当前列'''
	alien = Alien(ai_settings,screen)
	alien_width = alien.rect.width		
	alien.rect.x = alien_width + 2 * alien_width * alien_number
	alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
	alien.x = float(alien.rect.x)
	alien.y = float(alien.rect.y)
	aliens.add(alien)	

def create_fleet(ai_settings,screen,ship,aliens):
	'''创建外星人群'''
	#创建一个外星人并计算一行和一列可容纳多少个外星人
	#外星人间距为外星人宽度
	alien = Alien(ai_settings,screen)
	numbers_alien_x = get_number_aliens_x(ai_settings,alien.rect.width)
	number_rows = get_number_rows(ai_settings,ship.rect.height,alien.rect.height)

	#创建外星人群
	for row_number in range(number_rows):
		for alien_number in range(numbers_alien_x):
			#创建一个外星人并将其加入当前行
			#print(len(aliens))
			#for a in aliens:
			#	print(a.rect.x)
			create_alien(ai_settings,screen,aliens,alien_number,row_number)

def ship_hit(ai_settings,screen,stats,sb,ship,aliens,bullets):
	'''响应被外星人撞到的飞船'''
	#将ships_left减1
	if stats.ships_left > 0:
		stats.ships_left -= 1

		#更新计分牌
		sb.prep_ships()

		#清空外星人列表和子弹列表
		aliens.empty()
		bullets.empty()

		#创建一群新的外星人，并将飞船放在屏幕底端中央
		create_fleet(ai_settings,screen,ship,aliens)
		ship.center_ship()

		#暂停
		sleep(0.5)

	else:
		stats.game_active = False
		pygame.mouse.set_visible(True)

def update_aliens(ai_settings,screen,stats,sb,ship,aliens,bullets):
	'''检查是否有外星人位于屏幕边缘
	更新外星人中所有外星人的位置'''
	check_fleet_edges(ai_settings,aliens)
	aliens.update()

	#检测外星人和飞船之间的碰撞
	if pygame.sprite.spritecollideany(ship,aliens):
		print('SHIP HIT !!!')
		ship_hit(ai_settings,screen,stats,sb,ship,aliens,bullets)
		check_aliens_bottom(ai_settings,stats,sb,screen,ship,aliens,bullets)

def check_fleet_edges(ai_settings,aliens):
	'''有外星人到达边缘时采取相应措施'''
	for alien in aliens.sprites():
		if alien.check_edges():
			change_fleet_direction(ai_settings,aliens)
			break

def change_fleet_direction(ai_settings,aliens):
	'''将整群外星人下移，并改变他们的方向'''
	for alien in aliens.sprites():
		alien.rect.y +=	ai_settings.fleet_drop_speed
	ai_settings.fleet_direction *= -1

def check_aliens_bottom(ai_settings,stats,sb,screen,ship,aliens,bullets):
	#检查是否有外星人到达屏幕底端
	screen_rect = screen.get_rect()
	for alien in aliens.sprites():
		if alien.rect.bottom >= screen_rect.bottom:
			#像飞船被撞到一样进行处理
			ship_hit(ai_settings,stats,screen,sb,ship,aliens,bullets)
			break

def check_high_score(stats,sb):
	'''检查是否产生最高分'''
	if stats.score > stats.high_score:
		stats.high_score = stats.score
		sb.prep_high_score()