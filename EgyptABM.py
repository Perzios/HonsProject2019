from tkinter import *
import time
import numpy
import random
import math
import csv

class Patch:
    water = False
    fertility = 0
    settlement = False
    owned = False
    color = "yellow"
    population = 0
    farm = False
    harvested = False
    years_fallow = 0
    grain_payment = 0

class Household:
    def __init__(self, position_x, position_y, grain, workers, ambition, competency, workers_worked, generation_countdown, fields_owned, loyalty, num):
        self.position_x = position_x
        self.position_y = position_y
        self.grain = grain
        self.workers = workers
        self.ambition = ambition
        self.competency = competency
        self.workers_worked = workers_worked
        self.generation_countdown = generation_countdown
        self.fields_owned = fields_owned
        self.fields_coord = []
        self.ration_per_worker = 0
        self.consumed = False
        self.moved = False
        self.loyalty = loyalty
        self.prev_grain = 0
        self.output_line = [["Year", "Grain" , "Population", "Competency", "Ambition", "Loyalty"]]
        self.house_num = num

class Settlement:
    def __init__(self, num):
        self.output_line = [["Year", "Grain", "Population", "Households", "Average Competency", "Average Ambition", "Average Loyalty"]]
        self.house_num = num

class Globals:
    surplus = 0
    total_households = 0
    total_population = 0
    projected_historical_population = 0
    lorenz_points = 0
    avg_competency = 0
    avg_ambition = 0
    avg_loyalty = 0
    gini_index_reserve = 0
    output_lines = [["Year","Surplus", "Total Households", "Total Population", "Projected Historical Population", "Lorenz Points", "Average Competency", "Average Ambition", "Average Loyalty", "Gini Index Reserve"]]

class App(Frame):
        def __init__(self, master):
            Frame.__init__(self,master)
            self.grid()
            

            #Sets up the GUI
            self.menu_left = Frame(self, width=200, bg="grey")

            self.create_w()
            self.starting_workers()
            self.starting_settlements()
            self.starting_households()
            self.grain_cost_per_unit()
            self.starting_grain()
            self.min_ambition()
            self.min_comp()
            self.generational_variation()
            self.knowledge_radius()
            self.avg_yield_per_patch()
            self.fallow_limit()
            self.pop_growth_rate()
            self.worker_outsource_cut()
            self.worker_ration()
            self.min_loyaty()

            self.menu_left.pack(side="top", fill="both", expand=TRUE)

            self.canvas = Canvas(self, width=500,height=400,background="white")

            self.menu_left.grid(row=0, column=0, rowspan=2, sticky="nsew")
            self.canvas.grid(row=1, column=1, sticky="nsew")

            self.grid_rowconfigure(1, weight=1)
            self.grid_columnconfigure(1, weight=1)
            #end of GUI setup

        def create_w(self):
            self.label1 = Label(self.menu_left, text = "Year : 0")
            self.button1 = Button(self.menu_left)
            self.button1["text"] = "Go"
            self.button1["command"] = self.next_year
            self.button1.grid(row =0, column =0, columnspan =2, sticky =W)
            self.label1.grid(row=0, column=1, sticky=W)

            self.button3 = Button(self.menu_left)
            self.button3["text"] = "Go Repeating"
            self.button3["command"] = self.next_year_repeat
            self.button3.grid(row=17, column=0, columnspan=2, sticky=W)


            self.button2 = Button(self.menu_left)
            self.button2["text"] = "Setup"
            self.button2["command"] = self.setup
            self.button2.grid(row=16, column=0, sticky=W)

        #Setup settlements and households
        def setup(self):
            self.years = 0
            self.label1["text"] = "Year : " + str(self.years)

            #Array used to store the labels that make up the map
            self.labelsArr = numpy.empty(36, dtype=object)
            for i in range(36):
                self.labelsArr[i] = numpy.empty(36, dtype=object)

            #Array used to store patch information
            self.patchesArr = numpy.empty(36, dtype=object)
            for i in range(36):
                self.patchesArr[i] = numpy.empty(36, dtype=object)

            self.globalsVars = Globals()

            #Array used to store household info
            self.settlementArr = numpy.empty(self.startSettlements.get(), dtype=object)
            self.settlementArrOutput = numpy.empty(self.startSettlements.get(), dtype=object)
            for i in range(self.startSettlements.get()):
                self.settlementArr[i] = numpy.empty(self.startHouseholds.get(), dtype=object)
                self.settlementArrOutput[i] = Settlement(i)

            self.setup_patches()
            self.setup_settlements()
            self.globalsVars.total_households = self.startSettlements.get() * self.startHouseholds.get()

            for i in range(36):
                for j in range(36):
                    if j == 0:
                        self.patchesArr[i][j].color = "blue"
                        self.patchesArr[i][j].water = True
                        self.labelsArr[i][j] = Label(self.canvas, width=2, height=1, bg=self.patchesArr[i][j].color)
                        self.labelsArr[i][j].grid(row=i, column=j)
                    else:
                        self.labelsArr[i][j] = Label(self.canvas, width =2, height=1, bg=self.patchesArr[i][j].color)
                        self.labelsArr[i][j].grid(row=i, column=j)

        #Creates array of patches
        def setup_patches(self):
            for i in range(36):
                for j in range(36):
                    self.patchesArr[i][j] = Patch()

        #Places settlements
        def setup_settlements(self):
            counter = 0
            while counter < self.startSettlements.get():
                randX = random.randint(0, 35)
                randY = random.randint(1, 35)

                #checks if patch is free and if no other settlement too close
                if self.patchesArr[randX][randY].settlement is False and self.patchesArr[randX][randY].water is False and self.patchesArr[randX][randY].owned is False:
                    found = False
                    for x in range(5):
                        for y in range(5-x):
                            if (randX + x < 36 and randY + y < 36):
                                if (self.patchesArr[randX + x][randY + y].settlement is True):
                                    found = True
                            if (randX - x > 0 and randY + y < 36):
                                if (self.patchesArr[randX - x][randY + y].settlement is True):
                                    found = True
                            if (randX + x < 36 and randY - y > 0):
                                if (self.patchesArr[randX + x][randY - y].settlement is True):
                                    found = True
                            if (randX - x > 0 and randY - y > 0):
                                if (self.patchesArr[randX - x][randY - y].settlement is True):
                                    found = True
                    if found is False:
                        self.patchesArr[randX][randY].settlement = True
                        self.patchesArr[randX][randY].color = "cyan"
                        self.patchesArr[randX][randY].fertility = 0
                        self.setup_households(counter, randX, randY)
                        counter += 1

        #Populates settlementArr with households for each settlement
        def setup_households(self, counter, x, y):
            for i in range(self.startHouseholds.get()):
                grain = self.startGrain.get()
                workers = self.startWorkers.get()
                ambition = self.minAm.get() + random.uniform(0, 1 - self.minAm.get())
                competency = self.minComp.get() + random.uniform(0, 1 - self.minComp.get())
                loyalty = self.minLoyal.get() + random.uniform(0, 1 - self.minLoyal.get())
                workers_worked = 0
                gencountdown = random.randint(1, 6) + 10
                fields_owned = 0
                self.patchesArr[x][y].population += workers
                self.settlementArr[counter][i] = Household(x, y, grain, workers, ambition, competency, workers_worked, gencountdown, fields_owned , loyalty, counter)
                self.settlementArr[counter][i].ration_per_worker = ((grain/self.workerRation.get())/workers)
                #print(self.settlementArr[counter][i].ration_per_worker)

        def _from_rgb(self, rgb):
            """translates an rgb tuple of int to a tkinter friendly color code
            """
            return "#%02x%02x%02x" % rgb

        def update_patch_color(self):
            for i in range(36):
                for j in range(36):
                    self.labelsArr[i][j].config(bg=self.patchesArr[i][j].color)
                    #self.labelsArr[i][j].grid(row=i, column=j)

        #TODO GO REPEAT BUTTON
        def next_year_repeat(self):
            while self.years != 500 and self.globalsVars.total_households > 0:
                self.go()
                self.years += 1
                self.label1["text"] = "Year : " + str(self.years)
                print(self.globalsVars.total_households)
                print(self.globalsVars.total_population)

        #TODO GO BUTTON
        def next_year(self):
            if self.years < 500 and self.globalsVars.total_households > 0:
                self.go()
                self.years += 1
                self.label1["text"] = "Year : " + str(self.years)
                print(self.globalsVars.total_households)
                #Functionaltiy
                #self.modelTimeSpan.get() for slider values

        def go(self):
            self.flood()
            self.claim_lands()
            self.harvest_farms()
            self.harvest_other_farms()
            self.consume_grain()
            self.check_move()
            #self.storage_loss()
            self.field_changeover()
            self.generational_changeover()
            self.population_shift()
            #self.recolour_households()
            self.update_plot_values()
            self.output_globals()
            self.output_household_values()
            self.update_patch_color()
            self.update()
            for x in range(len(self.settlementArr)):
                print(len(self.settlementArr[x]))

        #; This method assigns a fertility value to each field based on its distance to water patches (ie: the Nile).
        def flood(self):
            mu = random.randint(1, 16) + 5
            sigma = random.randint(1, 6) + 5
            alpha = (2 * sigma ^ 2)
            beta = 1 / (sigma * math.sqrt(2 * math.pi))
            for i in range(36):
                for j in range(36):
                    if j !=0:
                        if (self.patchesArr[i][j].water is False) and (self.patchesArr[i][j].settlement is False):
                            self.patchesArr[i][j].fertility = 17 * (beta * (math.e ** (0 - (j - mu) ** 2 / alpha)))
                            #TODO code to change block colour according to fertility; check if we want to add it later?
                            temp = 40.0 * (self.patchesArr[i][j].fertility/1.3)
                            temp = 150 - temp
                            self.patchesArr[i][j].color = self._from_rgb((0, math.floor(temp), 0))
                            self.patchesArr[i][j].harvested = False

        #; This method allows households to decide whether or not to claim fields that fall within their knowledge-radii.
        #; The decision to claim is a function of distance to the field, the amount of grain needed to survive the walk, the fertility of the field, and ambition.
        #; It also sets ownership of fields (rendering them farms) to households that claim them.
        def claim_lands(self):
            for i in range(len(self.settlementArr)):
                for j in range(len(self.settlementArr[i])):
                    claimChance = random.uniform(0, 1)
                    self.settlementArr[i][j].prev_grain = self.settlementArr[i][j].grain
                    if (claimChance < self.settlementArr[i][j].ambition) or (self.settlementArr[i][j].fields_owned <= 1):  # ; decide if this household will be trying to claim land this tick
                        posX = self.settlementArr[i][j].position_x
                        posY = self.settlementArr[i][j].position_y
                        currGrain = self.settlementArr[i][j].grain
                        bestFertX = posX
                        bestFertY = posY
                        bestFertility = 0

                        for x in range(self.knowRad.get()):
                            for y in range(self.knowRad.get() - x):
                                distance = math.sqrt((x ** 2) + (y ** 2))
                                distanceFactor = distance * self.grainCost.get()
                                if (posX + x < 36 and posY + y < 36):
                                    if (self.patchesArr[posX + x][posY + y].settlement is False) and (self.patchesArr[posX + x][posY + y].water is False) and (self.patchesArr[posX + x][posY + y].owned is False):
                                        if (self.patchesArr[posX + x][posY + y].fertility > bestFertility) and (distanceFactor < currGrain):
                                            bestFertX = posX + x
                                            bestFertY = posY + y
                                            bestFertility = self.patchesArr[posX + x][posY + y].fertility
                                if (posX - x >= 0 and posY + y < 36):
                                    if (self.patchesArr[posX - x][posY + y].settlement is False) and (self.patchesArr[posX - x][posY + y].water is False) and (self.patchesArr[posX - x][posY + y].owned is False):
                                        if (self.patchesArr[posX - x][posY + y].fertility > bestFertility) and (distanceFactor < currGrain):
                                            bestFertX = posX - x
                                            bestFertY = posY + y
                                            bestFertility = self.patchesArr[posX - x][posY + y].fertility
                                if (posX + x < 36 and posY - y >= 0):
                                    if (self.patchesArr[posX + x][posY - y].settlement is False) and (self.patchesArr[posX + x][posY - y].water is False) and (self.patchesArr[posX + x][posY - y].owned is False):
                                        if (self.patchesArr[posX + x][posY - y].fertility > bestFertility) and (distanceFactor < currGrain):
                                            bestFertX = posX + x
                                            bestFertY = posY - y
                                            bestFertility = self.patchesArr[posX + x][posY - y].fertility
                                if (posX - x >= 0 and posY - y >= 0):
                                    if (self.patchesArr[posX - x][posY - y].settlement is False) and (self.patchesArr[posX - x][posY - y].water is False) and (self.patchesArr[posX - x][posY - y].owned is False):
                                        if (self.patchesArr[posX - x][posY - y].fertility > bestFertility) and (distanceFactor < currGrain):
                                            bestFertX = posX - x
                                            bestFertY = posY - y
                                            bestFertility = self.patchesArr[posX - x][posY - y].fertility

                        if (self.patchesArr[bestFertX][bestFertY].settlement is False) and (self.patchesArr[bestFertX][bestFertY].water is False) and (self.patchesArr[bestFertX][bestFertY].owned is False):
                            self.patchesArr[bestFertX][bestFertY].owned = True
                            self.patchesArr[bestFertX][bestFertY].farm = True
                            self.patchesArr[bestFertX][bestFertY].harvested = False
                            self.patchesArr[bestFertX][bestFertY].years_fallow = 0
                            self.settlementArr[i][j].fields_owned = self.settlementArr[i][j].fields_owned +1
                            self.settlementArr[i][j].fields_coord.append((bestFertX, bestFertY))
                            #TODO set field colour to match household; later maybe?
                            self.patchesArr[bestFertX][bestFertY].color = 'pink'

        def move(self, ambition, competence, loyalty):
            a = 0
            c = 0
            m = 0
            l = 0

            num = random.uniform(0, 1)
            if num < loyalty:
                return False

            if ambition >= 0.6:
                a = 1
            if competence >= 0.6:
                c = 1

            num = random.uniform(0, 1)

            if a == 1 and c == 1:
                if num <= 0.05:
                    m = 1
            elif a == 1 and c == 0:
                if num <= 0.3:
                    m = 1
            elif a == 0 and c == 1:
                if num <= 0.5:
                    m = 1
            elif a == 0 and c == 0:
                if num <= 0.9:
                    m = 1

            if m == 1:
                return True
            else:
                return False

        # ; Determines which farms are harvested each year. A household may only harvest one farm for each 2 workers they have.
        # ; For each  2 workers, the highest yield farm is found. The worker then decides whether they are ambitious and competent enough to harvest. A harvested farm is then marked with an 'H'.
        # ; Once a farm is harvested for the year, it may not be harvested again that year.
        # ; A 'seeding cost' is deducted; the seeding cost is calculated at 65kg/feddan; in the current setup, each patch is 200x200m, or 40,000m2.
        # ; A feddan = 4200m2, so each patch equals 9.52 feddans, so 9.52 * 65kg equals 618. If the layout of the world is changed, then the seeding cost will need to be recalculated.

        def harvest_farms(self):
            for i in range(len(self.settlementArr)):
                totalHarvest = 0
                for j in range(len(self.settlementArr[i])):
                    householdX = self.settlementArr[i][j].position_x
                    householdY = self.settlementArr[i][j].position_y
                    householdComp = self.settlementArr[i][j].competency
                    self.settlementArr[i][j].workers_worked = 0
                    for k in range(self.settlementArr[i][j].workers):   # was halved in newer model; 2 workers per patch
                        bestHarvest = 0
                        bestFieldX = 0
                        bestFieldY = 0
                        for l in range(self.settlementArr[i][j].fields_owned):
                            fieldX = self.settlementArr[i][j].fields_coord[l][0]
                            fieldY = self.settlementArr[i][j].fields_coord[l][1]
                            dist = math.sqrt(((householdX - fieldX) ** 2) + ((householdY - fieldY) ** 2))
                            thisHarvest = ((self.patchesArr[fieldX][fieldY].fertility * self.avgYpP.get() * householdComp) - (dist * self.grainCost.get()))
                            if (self.patchesArr[fieldX][fieldY].harvested is False) and (thisHarvest > bestHarvest):
                                bestHarvest = thisHarvest
                                bestFieldX = fieldX
                                bestFieldY = fieldY
                        farmChance = random.uniform(0, 1)
                        if (bestHarvest != 0):  # check that there is a field available
                            if (self.settlementArr[i][j].grain < (self.settlementArr[i][j].workers * self.workerRation.get())) or (farmChance < (self.settlementArr[i][j].ambition * self.settlementArr[i][j].competency)):
                                self.patchesArr[bestFieldX][bestFieldY].harvested = True
                                #TODO gui to mark field as harvested; later maybe?
                                self.patchesArr[bestFieldX][bestFieldY].color = 'red'
                                totalHarvest = totalHarvest + bestHarvest - 618  # ; 618 = cost of seeding the field (was 350 in newer model)
                                self.settlementArr[i][j].workers_worked = self.settlementArr[i][j].workers_worked + 1   # +2 added in newer model; 2 workers per patch
                for j in range(len(self.settlementArr[i])):
                    #print("im here now ", j)
                    if j == 0:
                        self.settlementArr[i][j].grain = self.settlementArr[i][j].grain + 0.2*totalHarvest + (totalHarvest*0.8)/len(self.settlementArr[i])
                    else:
                        self.settlementArr[i][j].grain = self.settlementArr[i][j].grain + (totalHarvest*0.8)/len(self.settlementArr[i])

        # ; Allows households to farm other households' unharvested fields. The owner of the farm takes a cut of the profits determined by the worker-outsource-cut.
        # ; Makes use of the same logic in harvest-farms.
        def harvest_other_farms(self):
            rented = False
            for i in range(len(self.settlementArr)):
                for j in range(len(self.settlementArr[i])):
                    totalHarvest = 0
                    householdX = self.settlementArr[i][j].position_x
                    householdY = self.settlementArr[i][j].position_y
                    householdComp = self.settlementArr[i][j].competency
                    for k in range(self.settlementArr[i][j].workers - self.settlementArr[i][j].workers_worked):
                        bestHarvest = 0
                        bestFieldX = 0
                        bestFieldY = 0

                        for x in range(self.knowRad.get()):
                            for y in range(self.knowRad.get() - x):
                                distance = math.sqrt((x ^ 2) + (y ^ 2))
                                distanceFactor = distance * self.grainCost.get()

                                #and (x, y) in self.settlementArr[i][j].fields_coord is False
                                if (householdX + x < 36 and householdY + y < 36):
                                    if (self.patchesArr[householdX + x][householdY + y].farm is True) and (self.patchesArr[householdX + x][householdY + y].harvested is False and (((x, y) in self.settlementArr[i][j].fields_coord) is False)):
                                        thisHarvest = ((self.patchesArr[householdX + x][householdY + y].fertility * self.avgYpP.get() * householdComp) - (distance * self.grainCost.get()))
                                        if (thisHarvest > bestHarvest):
                                            bestFieldX = householdX + x
                                            bestFieldY = householdY + y
                                            bestHarvest = thisHarvest
                                if (householdX - x > 0 and householdY + y < 36):
                                    if (self.patchesArr[householdX - x][householdY + y].farm is True) and (self.patchesArr[householdX - x][householdY + y].harvested is False and (((x, y) in self.settlementArr[i][j].fields_coord) is False)):
                                        thisHarvest = ((self.patchesArr[householdX - x][householdY + y].fertility * self.avgYpP.get() * householdComp) - (distance * self.grainCost.get()))
                                        if (thisHarvest > bestHarvest):
                                            bestFieldX = householdX - x
                                            bestFieldY = householdY + y
                                            bestHarvest = thisHarvest
                                if (householdX + x < 36 and householdY - y > 0):
                                    if (self.patchesArr[householdX + x][householdY - y].farm is True) and (self.patchesArr[householdX + x][householdY - y].harvested is False and (((x, y) in self.settlementArr[i][j].fields_coord) is False)):
                                        thisHarvest = ((self.patchesArr[householdX + x][householdY - y].fertility * self.avgYpP.get() * householdComp) - (distance * self.grainCost.get()))
                                        if (thisHarvest > bestHarvest):
                                            bestFieldX = householdX + x
                                            bestFieldY = householdY - y
                                            bestHarvest = thisHarvest
                                if (householdX - x > 0 and householdY - y > 0):
                                    if (self.patchesArr[householdX - x][householdY - y].farm is True) and (self.patchesArr[householdX - x][householdY - y].harvested is False and ((x, y) in self.settlementArr[i][j].fields_coord) is False):
                                        thisHarvest = ((self.patchesArr[householdX - x][ householdY - y].fertility * self.avgYpP.get() * householdComp) - (distance * self.grainCost.get()))
                                        if (thisHarvest > bestHarvest):
                                            bestFieldX = householdX - x
                                            bestFieldY = householdY - y
                                            bestHarvest = thisHarvest

                        farmChance = random.uniform(0, 1)
                        #print((bestFieldX, bestFieldY) in self.settlementArr[i][j].fields_coord)
                        if (bestHarvest != 0):  # check that there is a field that was found
                            if (farmChance < self.settlementArr[i][j].ambition * self.settlementArr[i][j].competency) and (self.settlementArr[i][j].grain > 618):
                                rented = True
                                self.patchesArr[bestFieldX][bestFieldY].harvested = True
                                # TODO gui to mark field as harvested; later maybe?
                                self.patchesArr[bestFieldX][bestFieldY].color = 'purple'
                                totalHarvest = totalHarvest + (bestHarvest * (self.workerOutSRC.get() / 100)) - 618  # ; 618 = cost of seeding the field
                                self.patchesArr[bestFieldX][bestFieldY].grain_payment = (bestHarvest * (1 - (self.workerOutSRC.get() / 100)))
                    self.settlementArr[i][j].grain = self.settlementArr[i][j].grain + totalHarvest
            if rented is True:  # gives rental payment to land owner
                for i in range(len(self.settlementArr)):
                    for j in range(len(self.settlementArr[i])):
                        for k in range(self.settlementArr[i][j].fields_owned):  # loop backwards so that removals don't break anything
                            if self.patchesArr[self.settlementArr[i][j].fields_coord[k][0]][self.settlementArr[i][j].fields_coord[k][1]].grain_payment > 0:
                                self.settlementArr[i][j].grain = self.settlementArr[i][j].grain + self.patchesArr[self.settlementArr[i][j].fields_coord[k][0]][self.settlementArr[i][j].fields_coord[k][1]].grain_payment
                                self.patchesArr[self.settlementArr[i][j].fields_coord[k][0]][self.settlementArr[i][j].fields_coord[k][1]].grain_payment = 0



        # decreases grain, kills a member if not enough grain, and remove household if no members
        def consume_grain(self):
            #print(len(self.settlementArr))
            for i in range(len(self.settlementArr)):
                for j in range(len(self.settlementArr[i]) - 1, -1, -1):  # loop backwards so that removals don't break anything
                    if self.settlementArr[i][j].consumed == False:
                        self.settlementArr[i][j].grain = self.settlementArr[i][j].grain - (self.settlementArr[i][j].workers * self.workerRation.get())

                        #print(self.settlementArr[i][j].grain, self.workerRation.get(), self.settlementArr[i][j].workers, self.settlementArr[i][j].ration_per_worker)
                        if self.settlementArr[i][j].grain <= 0:
                            self.settlementArr[i][j].grain = 0
                            self.settlementArr[i][j].workers = self.settlementArr[i][j].workers - 1
                            self.patchesArr[self.settlementArr[i][j].position_x][self.settlementArr[i][j].position_y].population = self.patchesArr[self.settlementArr[i][j].position_x][self.settlementArr[i][j].position_y].population + 1

                        # combined the storage loss function here since it seemed extra to have it as an additional function
                        self.settlementArr[i][j].grain = self.settlementArr[i][j].grain - (self.settlementArr[i][j].grain * 0.1)  # ; accounts for typical annual storage loss of agricultural product to storage-loss

                        self.settlementArr[i][j].consumed = True

                        if self.settlementArr[i][j].workers <= 0:
                            for k in range(self.settlementArr[i][j].fields_owned):
                                self.patchesArr[self.settlementArr[i][j].fields_coord[k][0]][self.settlementArr[i][j].fields_coord[k][1]].owned = False
                            if(len(self.settlementArr[i]) == 1):
                                self.patchesArr[self.settlementArr[i][j].position_x][self.settlementArr[i][j].position_y].settlement = False
                            tempArr = numpy.delete(self.settlementArr[i], j)
                            self.settlementArr[i] = tempArr
                        else:
                            self.settlementArr[i][j].ration_per_worker = ((self.settlementArr[i][j].grain / self.workerRation.get()) / self.settlementArr[i][j].workers)
                            if self.settlementArr[i][j].grain >= self.settlementArr[i][j].prev_grain:
                                self.settlementArr[i][j].loyalty += 0.02
                                if self.settlementArr[i][j].loyalty >= 1.0:
                                    self.settlementArr[i][j].loyalty = 1.0
                            else:
                                self.settlementArr[i][j].loyalty -= 0.02
                                if self.settlementArr[i][j].loyalty <= 0.0:
                                    self.settlementArr[i][j].loyalty = 0.0



            for i in range(len(self.settlementArr)):
                for j in range(len(self.settlementArr[i]) - 1, -1, -1):
                    self.settlementArr[i][j].consumed = False

        def check_move(self):
            for i in range(len(self.settlementArr)):
                for j in range(len(self.settlementArr[i]) - 1, -1, -1):
                    if self.settlementArr[i][j].ration_per_worker <= 2.5 and self.settlementArr[i][j].moved == False:
                        willMove = self.move(self.settlementArr[i][j].ambition, self.settlementArr[i][j].competency , self.settlementArr[i][j].loyalty)
                        if willMove is True:
                            bestI = 999
                            bestGrain = 0
                            y = 0
                            #print(len(self.settlementArr))
                            for x in range(len(self.settlementArr)):
                                #print(x, y, i, j)
                                if len(self.settlementArr[x]) > 0:
                                    if x != i:
                                        if self.settlementArr[x][y].grain > bestGrain:
                                            bestGrain = self.settlementArr[x][y].grain
                                            bestI = x

                            if bestGrain >= 1.2 * self.settlementArr[i][j].grain and bestI != 999:
                                posX = self.settlementArr[i][j].position_x
                                posY = self.settlementArr[i][j].position_y
                                self.settlementArr[i][j].moved = True
                                self.settlementArr[i][j].grain = self.settlementArr[i][j].grain * 0.85

                                self.settlementArr[i][j].position_x = self.settlementArr[bestI][0].position_x
                                self.settlementArr[i][j].position_y = self.settlementArr[bestI][0].position_y
                                temp = numpy.append(self.settlementArr[bestI], self.settlementArr[i][j])
                                self.settlementArr[bestI] = temp
                                print("I moved", i, j , "to" , bestI)
                                if j == 0 and len(self.settlementArr[i]) == 1:
                                    self.patchesArr[posX][posY].settlement = False
                                tempArr = numpy.delete(self.settlementArr[i], j)
                                self.settlementArr[i] = tempArr

            for i in range(len(self.settlementArr)):
                for j in range(len(self.settlementArr[i]) - 1, -1, -1):
                    self.settlementArr[i][j].moved = False

        # ; allows fields that have lay fallow for a certain number of years to be forfeited for claim by other households to field-changeover
        def field_changeover(self):
            removal = False
            for i in range(36):
                for j in range(36):
                    if self.patchesArr[i][j].farm is True:
                        if self.patchesArr[i][j].harvested is True:
                            self.patchesArr[i][j].years_fallow = 0
                        else:
                            self.patchesArr[i][j].years_fallow = self.patchesArr[i][j].years_fallow + 1
                        if self.patchesArr[i][j].years_fallow > self.fallowLim.get():
                            removal = True
                            self.patchesArr[i][j].owned = False
                            self.patchesArr[i][j].farm = False
            # loop through households to remove fields that are no longer owned
            if removal is True:
                for i in range(len(self.settlementArr)):
                    for j in range(len(self.settlementArr[i])):
                        for k in range(self.settlementArr[i][j].fields_owned - 1, -1, -1):  # loop backwards so that removals don't break anything
                            if self.patchesArr[self.settlementArr[i][j].fields_coord[k][0]][self.settlementArr[i][j].fields_coord[k][1]].owned is False:
                                self.settlementArr[i][j].fields_owned = self.settlementArr[i][j].fields_owned - 1
                                self.settlementArr[i][j].fields_coord.remove(self.settlementArr[i][j].fields_coord[k])

        # on generational changeover, resets its count and recalculates ambition and competence
        def generational_changeover(self):
            for i in range(len(self.settlementArr)):
                for j in range(len(self.settlementArr[i])):
                    self.settlementArr[i][j].generation_countdown = self.settlementArr[i][j].generation_countdown - 1
                    if self.settlementArr[i][j].generation_countdown <= 0:
                        self.settlementArr[i][j].generation_countdown = random.randint(1, 6) + 10

                        ambitionChange = random.uniform(0, self.genVar.get())
                        decreaseChance = random.uniform(0, 1)
                        if decreaseChance < 0.5:
                            ambitionChange = ambitionChange * (-1)
                        newAmbition = self.settlementArr[i][j].ambition + ambitionChange
                        while (newAmbition > 1) or (newAmbition < self.minAm.get()):
                            ambitionChange = random.uniform(0, self.genVar.get())
                            decreaseChance = random.uniform(0, 1)
                            if decreaseChance < 0.5:
                                ambitionChange = ambitionChange * (-1)
                            newAmbition = self.settlementArr[i][j].ambition + ambitionChange
                        self.settlementArr[i][j].ambition = newAmbition

                        competenceChange = random.uniform(0, self.genVar.get())
                        decreaseChance = random.uniform(0, 1)
                        if decreaseChance < 0.5:
                            competenceChange = competenceChange * (-1)
                        newCompetence = self.settlementArr[i][j].competency + competenceChange
                        while (newCompetence > 1) or (newCompetence < self.minComp.get()):  # minCompetence was input in gui
                            competenceChange = random.uniform(0, self.genVar.get())
                            decreaseChance = random.uniform(0, 1)
                            if decreaseChance < 0.5:
                                competenceChange = competenceChange * (-1)
                            newCompetence = self.settlementArr[i][j].competency + competenceChange
                        self.settlementArr[i][j].competency = newCompetence

        # ;allows for population maintenance as households 'die', simulating a movement of workers from failed households to more successful households
        # ;as well as more natural population increase (higher birth-rate vs death-rate)
        # ;but to keep the overall population density and growth to within reasonable limits that correlate with those projected by historians and archaeologists,
        # ;who reconstruct a less than .1% annual population growth for Egypt in the predynastic.
        # ;since the landscape abstracted here represents the more fertile parts of ancient egypt,
        # ;one might expect greater growth here than the average for all of Egypt, which is why the equation below allows a cushion of 2 * the pop-growth-rate parameter.
        def population_shift(self):
            startingPopulation = self.startSettlements.get() * self.startHouseholds.get() * self.startWorkers.get()
            for i in range(len(self.settlementArr)):
                for j in range(len(self.settlementArr[i])):
                    populateChance = random.uniform(0, 1)
                    if (populateChance < self.settlementArr[i][j].ambition * self.settlementArr[i][j].competency) and (self.settlementArr[i][j].grain > (self.settlementArr[i][j].workers * self.workerRation.get())) and (self.globalsVars.total_population < (startingPopulation * (1 + 2 * (self.popGR.get() / 100)) ** self.years)):
                        self.settlementArr[i][j].workers = self.settlementArr[i][j].workers + 1
                        self.patchesArr[self.settlementArr[i][j].position_x][self.settlementArr[i][j].position_y].population = self.patchesArr[self.settlementArr[i][j].position_x][self.settlementArr[i][j].position_y].population + 1
            self.globalsVars.projected_historical_population = startingPopulation * (1.001) ** self.years  # ; to compare with archaelogical estimates of population growth for this period

        # ;; Set the class of the households -- if a household has less than a third
        # ;; the wealth of the richest household, color it yellow.  If between one
        # ;; and two thirds, color it turquoise.  If over two thirds, color it magenta.
        # ;; this code adapted from 'wealth distribution model' in Netlogo model library to recolor-households
        def recolour_households(self):  #TODO GUI stuff, we can maybe leave out this function though
            max_grain = 0
            for i in range(len(self.settlementArr)):
                for j in range(len(self.settlementArr[i])):
                    if self.settlementArr[i][j].grain > maxGrain:
                        maxGrain = self.settlementArr[i][j].grain
            for i in range(len(self.settlementArr)):
                for j in range(len(self.settlementArr[i])):
                    if (self.settlementArr[i][j].grain <= (maxGrain / 3)):
                        i = 0  # remove later
                        # set colour to yellow
                    elif (self.settlementArr[i][j].grain <= (maxGrain * 2 / 3)):
                        i = 0  # remove later
                        # set colour to turquoise
                    else:
                        i = 0  # remove later
                        # set colour to magenta

        # updates values that got added to line graph, we can use this to produce an output later
        def update_plot_values(self):
            self.globalsVars.surplus = 0
            self.globalsVars.total_households  = 0
            self.globalsVars.total_population  = 0
            totalAmbition = 0
            totalCompetence = 0
            totalLoyalty = 0
            startingPopulation = self.startSettlements.get() * self.startHouseholds.get() * self.startWorkers.get()
            sortedWealths = []
            for i in range(len(self.settlementArr)):
                for j in range(len(self.settlementArr[i])):
                    self.globalsVars.surplus = self.globalsVars.surplus + self.settlementArr[i][j].grain
                    self.globalsVars.total_households = self.globalsVars.total_households + 1
                    self.globalsVars.total_population = self.globalsVars.total_population + self.settlementArr[i][j].workers
                    totalAmbition = totalAmbition + self.settlementArr[i][j].ambition
                    totalCompetence = totalCompetence + self.settlementArr[i][j].competency
                    totalLoyalty = totalLoyalty + self.settlementArr[i][j].loyalty
                    sortedWealths.append(self.settlementArr[i][j].grain)

            if self.globalsVars.total_households > 0:
                self.globalsVars.avg_ambition = totalAmbition / self.globalsVars.total_households
                self.globalsVars.avg_competency = totalCompetence / self.globalsVars.total_households
                self.globalsVars.avg_loyalty = totalLoyalty / self.globalsVars.total_households

            sortedWealths.sort()
            wealthSum = 0
            self.globalsVars.gini_index_reserve = 0.0
            self.globalsVars.lorenz_points = []
            for i in range(self.globalsVars.total_households):
                wealthSum = wealthSum + sortedWealths[i]
                if self.globalsVars.surplus > 0:
                    self.globalsVars.lorenz_points.append((wealthSum / self.globalsVars.surplus) * 100)
                    self.globalsVars.gini_index_reserve = self.globalsVars.gini_index_reserve + ((i + 1) / self.globalsVars.total_households) - (wealthSum / self.globalsVars.surplus)

        def output_globals(self):
            line = [(self.years+1), self.globalsVars.surplus, self.globalsVars.total_households, self.globalsVars.total_population, self.globalsVars.projected_historical_population, self.globalsVars.lorenz_points, self.globalsVars.avg_competency, self.globalsVars.avg_ambition,self.globalsVars.avg_loyalty , self.globalsVars.gini_index_reserve]
            self.globalsVars.output_lines.append(line)
            with open('GlobalOutput.csv', 'w') as writeFile:
                writer = csv.writer(writeFile)
                writer.writerows(self.globalsVars.output_lines)
            writeFile.close()

        #[["Year", "Grain", "Population", "Households", "Average Competency", "Average Ambition", "Average Loyalty"]]
        def output_household_values(self):
            for i in range(len(self.settlementArr)):
                grain = 0
                pop = 0
                total_households = len(self.settlementArr[i])
                avg_loyalty = 0
                avg_comp = 0
                avg_Amb = 0
                for j in range(total_households):
                    grain += self.settlementArr[i][j].grain
                    pop += self.settlementArr[i][j].workers
                    avg_Amb = avg_Amb + self.settlementArr[i][j].ambition
                    avg_comp = avg_comp + self.settlementArr[i][j].competency
                    avg_loyalty = avg_loyalty + self.settlementArr[i][j].loyalty
                    self.household_print(self.settlementArr[i][j])

                if total_households > 0:
                    avg_Amb = avg_Amb / total_households
                    avg_comp = avg_comp / total_households
                    avg_loyalty = avg_loyalty / total_households

                line = [(self.years + 1), grain, pop, total_households, avg_comp, avg_Amb, avg_loyalty]
                self.settlementArrOutput[i].output_line.append(line)
                name = ("village%d.csv" % self.settlementArrOutput[i].house_num)
                with open(name, 'w') as writeFile:
                    writer = csv.writer(writeFile)
                    writer.writerows(self.settlementArrOutput[i].output_line)
                writeFile.close()


        def household_print(self, house):
            #[["Year", "Grain" , "Population", "Competency", "Ambition", "Loyalty"]]
            line = [(self.years+1), house.grain, house.workers, house.competency, house.ambition, house.loyalty]
            house.output_line.append(line)
            name = ("household%d.csv" % house.house_num)
            with open(name, 'w') as writeFile:
                writer = csv.writer(writeFile)
                writer.writerows(house.output_line)
            writeFile.close()


# --------------------------- GUI element definitions start here here ---------------------------
        def starting_settlements(self):
            self.label3 = Label(self.menu_left, text = "Starting-settlements")
            self.label3.grid(row=2, column=0, sticky=W)
            self.startSettlements = Scale(self.menu_left, from_ =1, to=40, orient =HORIZONTAL)
            self.startSettlements.grid(row =2, column=1, sticky =W)
            self.startSettlements.set(15)

        def starting_households(self):
            self.label4 = Label(self.menu_left, text = "Starting-households")
            self.label4.grid(row=1, column=0, sticky=W)
            self.startHouseholds = Scale(self.menu_left, from_ =1, to=1, orient =HORIZONTAL)
            self.startHouseholds.grid(row =1, column=1, sticky =W)

        def starting_workers(self):
            self.label2 = Label(self.menu_left, text="Starting-workers")
            self.label2.grid(row=3, column=0, sticky=W)
            self.startWorkers = Scale(self.menu_left, from_=1, to=30, orient=HORIZONTAL)
            self.startWorkers.grid(row=3, column=1, sticky=W)
            self.startWorkers.set(10)

        def avg_yield_per_patch(self):
            self.label4 = Label(self.menu_left, text = "Average-yield-per-patch")
            self.label4.grid(row=5, column=0, sticky=W)
            self.avgYpP = Scale(self.menu_left, from_ =1000, to=4000, resolution = 25, orient =HORIZONTAL)
            self.avgYpP.grid(row =5, column=1, sticky =W)
            self.avgYpP.set(2776)

        def starting_grain(self):
            self.label5 = Label(self.menu_left, text = "Starting-grain")
            self.label5.grid(row=4, column=0, sticky=W)
            self.startGrain = Scale(self.menu_left, from_ =100, to=7500,resolution =100, orient =HORIZONTAL)
            self.startGrain.grid(row =4, column=1, sticky =W)
            self.startGrain.set(7500)

        def min_ambition(self):
            self.label6 = Label(self.menu_left, text = "Min-Ambition")
            self.label6.grid(row=6, column=0, sticky=W)
            self.minAm = Scale(self.menu_left, from_ =0.1, to=1.0 , digits=2, resolution = 0.1, orient =HORIZONTAL)
            self.minAm.grid(row =6, column=1, sticky =W)

        def min_comp(self):
            self.label7 = Label(self.menu_left, text = "Min-competency")
            self.label7.grid(row=7, column=0, sticky=W)
            self.minComp = Scale(self.menu_left, from_ =0.1, to=1.0, digits=2, resolution = 0.1, orient =HORIZONTAL)
            self.minComp.grid(row =7, column=1, sticky =W)

        def generational_variation(self):
            self.label8 = Label(self.menu_left, text="Generational-variation")
            self.label8.grid(row=8, column=0, sticky=W)
            self.genVar = Scale(self.menu_left, from_=0.05, to=1.0, digits=2, resolution=0.05, orient=HORIZONTAL)
            self.genVar.grid(row=8, column=1, sticky=W)
            self.genVar.set(1.0)

        def knowledge_radius(self):
            self.label9 = Label(self.menu_left, text="Knowledge-radius")
            self.label9.grid(row=9, column=0, sticky=W)
            self.knowRad = Scale(self.menu_left, from_=1, to=100, orient=HORIZONTAL)
            self.knowRad.grid(row=9, column=1, sticky=W)
            self.knowRad.set(100)

        def grain_cost_per_unit(self):
            self.label10 = Label(self.menu_left, text="Grain-cost-per-unit(kg)")
            self.label10.grid(row=10, column=0, sticky=W)
            self.grainCost = Scale(self.menu_left, from_=1, to=15, orient=HORIZONTAL)
            self.grainCost.grid(row=10, column=1, sticky=W)
            self.grainCost.set(8)

        def fallow_limit(self):
            self.label11 = Label(self.menu_left, text="Fallow-limit(years)")
            self.label11.grid(row=11, column=0, sticky=W)
            self.fallowLim = Scale(self.menu_left, from_=1, to=10, orient=HORIZONTAL)
            self.fallowLim.grid(row=11, column=1, sticky=W)
            self.fallowLim.set(3)

        def pop_growth_rate(self):
            self.label12 = Label(self.menu_left, text="Pop-growth-rate(%)")
            self.label12.grid(row=12, column=0, sticky=W)
            self.popGR = Scale(self.menu_left, from_=0.01, to=0.20, digits=2, resolution = 0.01, orient=HORIZONTAL)
            self.popGR.grid(row=12, column=1, sticky=W)
            self.popGR.set(0.1)

        def worker_ration(self):
            self.label13 = Label(self.menu_left, text="Worker-ration(kg)")
            self.label13.grid(row=13, column=0, sticky=W)
            self.workerRation = Scale(self.menu_left, from_=10, to=500, resolution=10, orient=HORIZONTAL)
            self.workerRation.grid(row=13, column=1, sticky=W)
            self.workerRation.set(160)

        def worker_outsource_cut(self):
            self.label13 = Label(self.menu_left, text="Worker-outsource-cut(%)")
            self.label13.grid(row=14, column=0, sticky=W)
            self.workerOutSRC = Scale(self.menu_left, from_=5, to=100, resolution=5, orient=HORIZONTAL)
            self.workerOutSRC.grid(row=14, column=1, sticky=W)
            self.workerOutSRC.set(35)

        def min_loyaty(self):
            self.label14 = Label(self.menu_left, text = "Min-Loyalty")
            self.label14.grid(row=15, column=0, sticky=W)
            self.minLoyal = Scale(self.menu_left, from_ =0.1, to=1.0, digits=2, resolution = 0.1, orient =HORIZONTAL)
            self.minLoyal.grid(row =15, column=1, sticky =W)
            self.minLoyal.set(0.4)


# --------------------------- GUI element definitions end here here ---------------------------

#THIS NEEDS TO BE AT BOTTOM
root = Tk()
root.title("Egypt")
#root.geometry("600x200")

app = App(root)

root.mainloop()