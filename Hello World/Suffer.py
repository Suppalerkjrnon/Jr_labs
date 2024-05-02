class Hello_world:
    def suffer(self):
        self.char1 = 'H'
        self.char2 = 'E'
        self.char3 = 'L'
        self.char4 = 'L'
        self.char5 = 'O'
        self.char6 = 'W'
        self.char7 = 'O'
        self.char8 = 'R'
        self.char9 = 'L'
        self.char10 = 'D'
        self.array = list()

        self.between = ' '
        self.exclation = '!'

    def suffer2(self):
        for i in range(1, 11): #range doesn't include the last number
            self.array.append('char' + str(i)) #Append that string number to the array
        
        return self.array

    def suffer3(self):
        self.array.insert(5, self.between) #Insert str into the array at index [5]
        self.array.append(self.exclation) # Append the exclamation mark to the array

        return self.array


    def suffer4(self):
        hello_world = '' 
        for item in self.array: #Iterate each item in the array
            if item.startswith('char'): #If the item starts with 'char' we got from self.array which is self.char!
                hello_world += getattr(self, item) #Get the value of the attribute from the object 
            else:
                hello_world += item # If it's not a char then turn it into a string

        print(hello_world)

if __name__ == '__main__':
    hello = Hello_world()
    hello.suffer()
    hello.suffer2()
    hello.suffer3()
    hello.suffer4()

