import pygame, heapq


class Cell():
	# Les carrés qui consituent le plan
	def __init__(self, est_mur: bool) -> None:
		self.f_score = float('inf')         # le coût de déplacement
		self.g_score = 0                    # le coût de déplacement estimé
		self.h_score = 0                    # le coût de déplacement total = g_score + h_score

		self.x = 0                          # coordonée x en pixel
		self.y = 0                          # coordonée y en pixel

		self.i = 0                          # indice i de cellule
		self.j = 0                          # indice j de cellule
		self.parent_i = None                # indice i de parent
		self.parent_j = None                # indice j de parent
		self.dim = 1                        # dimension du carré en pixel
		self.est_mur = bool(est_mur)        # indiquer si cette cellule est le mur ou pas (True ou False)


##################################################


def est_valide(plan, i, j) -> bool:
	"""
	Véifier si les coordonnées sont bien dans le plan
	:param
		- plan: une liste 2D des cellules (forme carrée), list
		- i: indice i, int
		- j: indice j, int
	:return
		Booléen
	"""
	return i >= 0 and j < len(plan) and j >= 0 and i < len(plan)


def trouver_indices_cell(plan, x, y) -> object:
	"""
	Trouver les indices de la cellule auquel la position correspond
	:param
		- plan: une liste 2D des cellules (forme carrée), list
		- x: position en x, int
		- y: position en y, int
	:return
		les indices de la cellule, int
	"""
	trouve = False
	i,j = 0,0
	while i < len(plan) and not trouve:
		j = 0
		while j < len(plan) and not trouve:
			cell = plan[i][j]
			if (cell.x <= x < cell.x + cell.dim) and (cell.y <= y < cell.y + cell.dim): # attention la comparaison
				return i, j
			j += 1
		i += 1

	return i-1, j-1

def indices_en_coordonnees(i, j, dim):
	"""
	Trouver les coordonées d'une cellule à partir de ses indices
	:param
		- i: indice i, int
		- j: indice j, int
	:return
		- x: coordonée x, int
		- y: coordonée y, int
	"""
	return j*dim, i*dim


def est_cell_destination(i, j, dest) -> bool:
	"""
	La fonction vérifie si la position est déjà la destination
	:param
		- dest: cellule de destination, object
		- i: indice i, int
		- j: indice j, int
	:return
		Booléen
	"""
	return (i == dest.i and j == dest.j)


def calcul_h_score(cell, dest) -> float:
	"""
	La fonction qui calcule la distance à vol d'oiseau entre la cellule considéré
	et la cellule de destination
	:param
		- dest: cellule de destination, object
		- cell: cellule considéré, objet
	:return
		la distance à vol d'oiseau entre les cellules considéré
	"""
	return ((cell.x - dest.x)**2 + (cell.y - dest.y)**2)**(1/2)


def tracer_le_chemin(plan, pos_i, pos_f, dest) -> list:
	"""
	Tracer le chemin de la cellule de depart à celle de destination
	:param
		- plan: une liste 2D des cell (forme carrée), list
		- pos_i: position initiale (du robot)
		- pos_f: position finale (où l'on clique)
		- dest: cellule de la destination, object
	:return
		une liste des cellules liées entre eux du depart à la destination
	"""
	chemin = [pos_f]
	row = dest.i
	col = dest.j
	dim = dest.dim

	# Tracer le chemin de la destination à la source à l'aide des cellules parentes (cell.parent)
	while plan[row][col].parent_i != None:
		chemin.append(indices_en_coordonnees(row, col, dim))
		temp_row = plan[row][col].parent_i
		temp_col = plan[row][col].parent_j
		row = temp_row
		col = temp_col

	# Ajouter la position de la cellule de source et la position initiale au chemin
	chemin.append(indices_en_coordonnees(row, col, dim))
	chemin.append(pos_i)
	
	chemin.reverse()

	return chemin


def a_star(plan, pos_i, pos_f) -> list:
	"""
	Utiliser l'algorithme de A Star pour trouver le chemin le plus court entre
	2 position.
	:param
		- plan: une liste 2D des cell (forme carrée), list 
		- pos_i: position initiale (du robot)
		- pos_f: position finale (où l'on clique)
	:return
		une liste des cellules liées entre eux du depart à la destination
	"""
	
	if pos_i == pos_f: #Vérifier si on est déjà sur la cellule de la destination
		return 

	i_src, j_src = trouver_indices_cell(plan, pos_i[0], pos_i[1])
	i_dest, j_dest = trouver_indices_cell(plan, pos_f[0], pos_f[1])

	dest = plan[i_dest][j_dest]  # la cellule de destination

	if dest.est_mur: #Vérifier si la destination est mur
		print("C'est le mur")
		return
	
	# Initialier la liste fermée (cellules ont été visitées) :
	closed_list = [[False for _ in range(len(plan))] for _ in range(len(plan))]

	# Initialiser la liste ouverte (cellules à visiter) avec la cellule de source :
	open_list = [] 
	heapq.heappush(open_list, (0, i_src, j_src))

	# Boucle principale de A* algorithme :
	while len(open_list) > 0:
		# Pop la cellule avec la plus petite valeur f de la liste ouverte : 
		p = heapq.heappop(open_list)

		# Marquer la cellule comme visitée :
		i = p[1]
		j = p[2]
		closed_list[i][j] = True

		# Les directions possibles : 
		directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
		for dir in directions:
			i_new = i + dir[0]
			j_new = j + dir[1]
			
			# Vérifier si le successeur est valide, n'est pas le mur et non visité :
			if est_valide(plan, i_new, j_new) and not plan[i_new][j_new].est_mur and not closed_list[i_new][j_new]:

				suc = plan[i][j]            # successeur
				pré = plan[i_new][j_new]    # prédécesseur

				# Si c'est la destination : 
				if est_cell_destination(i_new, j_new, dest):
					# Définir le parent de la cellule
					pré.parent_i = i
					pré.parent_j = j

					print("La destionation est trouvée")
					found_dest = True
					return tracer_le_chemin(plan, pos_i, pos_f, dest)
				
				else:
					# Calculer f, g, et h scores :  
					g_new = suc.g_score + 1   #có thể tạo thêm bộ nhớ ở đây để giảm thời gian chạy toàn list tìm cell
					h_new = calcul_h_score(suc, dest)
					f_new = g_new + h_new

					# Si la cellule n'est pas dans la liste ouverte ou si la nouvelle valeur f est inférieure à l'ancienne valeur.
					if pré.f_score > f_new:
						# Ajouter la cellule à la liste ouverte :
						heapq.heappush(open_list, (f_new, i_new, j_new))
						# Mettre à jour les descriptions de la cellule :
						pré.f_score = f_new
						pré.g_score = g_new
						pré.h_score = h_new
						pré.parent_i = i
						pré.parent_j = j


def creer_plan(grid, dim) -> list:
	"""
	Créer un plan des cellules à partir d'un grid
	:param
		- grid: liste 2D des booléenes, 1 si la cellule est mur 0 sinon, list
		- dim: dimension d'une cellule, int
	:return
		- plan: liste 2D des cellules
	"""
	plan = []
	for i in range(len(grid)):
		row_plan = []
		for j in range(len(grid)):
			# initialiser la cellule : 
			cell = Cell(grid[i][j])
			cell.dim = dim
			
			cell.i = i; cell.j = j
			cell.y = i*cell.dim; cell.x = j*cell.dim # attention y est vertical

			row_plan.append(cell)
		plan.append(row_plan)
		
	return plan


# def main():
# 	# Definir le grid (1 est mur, 0 est libre)
# 	grid = [
# 		[0, 1, 0, 0, 0, 0, 1, 0, 0, 0],
# 		[0, 0, 0, 1, 0, 0, 0, 1, 0, 0],
# 		[0, 0, 0, 1, 0, 0, 1, 0, 1, 0],
# 		[1, 1, 0, 1, 0, 1, 1, 1, 1, 0],
# 		[0, 0, 0, 1, 0, 0, 0, 1, 0, 1],
# 		[0, 1, 0, 0, 0, 0, 1, 0, 1, 1],
# 		[0, 1, 1, 1, 1, 0, 1, 1, 1, 0],
# 		[0, 1, 0, 0, 0, 0, 1, 0, 0, 0],
# 		[0, 0, 0, 1, 1, 1, 0, 1, 1, 0]
# 	]
	
# 	# Définir la source et la destination :
# 	src = 0, 8      # coordonnées (x,y)
# 	dest = 0, 0
# 	dim = 2

# 	plan = creer_plan(grid, dim)
# 	# Exécutez l'algorithme de recherche A* : 
# 	print(a_star(plan, src, dest))

# if __name__ == "__main__":
	main()