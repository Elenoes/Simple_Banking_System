#  5304 46 02 1234 567  8
#  __iin__|__acc_id___|chk
import random
import sqlite3


class CreditCard():
    def __init__(self):
        self.iin = 400000
        self.acc_id = None
        self.checksum = None
        self.pin = None
        self.balance = None

    def luhn_algorithm(self):
        card_number = list(f"{self.iin}{self.acc_id}")
        card_number = [int(x) for x in card_number]

        for x in range(0,len(card_number),2):
            card_number[x] = card_number[x] * 2 if card_number[x] * 2 <= 9 else (card_number[x] * 2) - 9
        self.checksum = 0 if sum(card_number) % 10 == 0 else 10 - (sum(card_number) % 10)

        return self.checksum

    def create_cred_card(self):
        self.acc_id = random.randint(100000000, 999999999)
        self.checksum = CreditCard.luhn_algorithm(self)
        self.pin = random.randint(1000, 9999)
        self.acc = f"{self.iin}{self.acc_id}{self.checksum}"
        self.balance = 0
    




def main():
    conn = sqlite3.connect('card.s3db')
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS card (id INTEGER PRIMARY KEY, number text, pin text, balance INTEGER DEFAULT 0);")
    while True:
        inp_choice = input("1. Create an account\n2. Log into account\n0. Exit\n")

        if inp_choice == "1":
            crCard = CreditCard()
            crCard.create_cred_card()
            print("Your card number: \n{}".format(crCard.acc))
            print("Your card PIN: \n{}".format(crCard.pin))
            cur.execute(f"INSERT INTO card(number, pin) VALUES ({crCard.acc}, {crCard.pin})")
            conn.commit()
        elif inp_choice == "2":
            card_num = input("Enter your card number:")
            pin = input("Enter your PIN:")

            cur.execute(f"select * from card where card.number = {card_num} and card.pin = {pin}")
            selected_card = None
            selected_card = cur.fetchone()


            if selected_card:
                print("You have successfully logged in!\n")
                inp_operation = None
                while True and inp_operation != 4:
                    inp_operation = input("1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit\n")
                
                    if inp_operation == "1":
                        cur.execute(f"select * from card where card.number = {card_num} and card.pin = {pin}")      # this select needed because balance can change and I need to monitor it
                        selected_card = cur.fetchone()                        
                        print("Balance: {}".format(selected_card[3]))                   
                    elif inp_operation == "2":
                        income = input("Enter income:")
                        cur.execute(f"select * from card where card.number = {card_num} and card.pin = {pin}")      # this select needed because balance can change and I need to monitor it
                        selected_card = cur.fetchone()    
                        cur.execute(f"update card set balance = {int(income) + selected_card[3]} where card.number = {card_num} and card.pin = {pin}")
                        conn.commit()
                        print("Income was added!")
                    elif inp_operation == "3":
                        print("Transfer")
                        inp_card_number = input("Enter card number:")

                        cur.execute(f"select * from card where card.number = {inp_card_number}")
                        receiver_card = None
                        receiver_card = cur.fetchone()

                        if receiver_card:
                            checked_cr_card = CreditCard()
                            checked_cr_card.iin = 400000
                            checked_cr_card.acc_id = receiver_card[1][6:15]
                            checked_cr_card_checksum = checked_cr_card.luhn_algorithm()

                            cur.execute(f"select * from card where card.number = {card_num} and card.pin = {pin}")      # this select needed because balance can change and I need to monitor it
                            selected_card = cur.fetchone()

                            if receiver_card[1] == card_num:
                                print("You can't transfer money to the same account!\n")
                            elif int(receiver_card[1][-1]) != int(checked_cr_card.luhn_algorithm()):
                                print("Probably you made a mistake in the card number. Please try again!\n")                         
                            else:
                                hm_money = input("Enter how much money you want to transfer:")
                                if int(selected_card[3]) >= int(hm_money):
                                    cur.execute(f"update card set balance = {receiver_card[3] + int(hm_money)} where card.number = {inp_card_number}")
                                    conn.commit()
                                    cur.execute(f"update card set balance = {selected_card[3] - int(hm_money)} where card.number = {card_num}")
                                    conn.commit()
                                    print("Success\n")
                                else:
                                    print("Not enough money!\n")
                        else:
                            print("Such a card does not exist.\n")                                    
                            
                    elif inp_operation == "4":
                        cur.execute(f"delete from card where card.number={card_num} and card.pin = {pin}")
                        conn.commit()
                        print("The account has been closed!\n")
                        break


                    elif inp_operation == "5":
                        print("You have successfully logged out! \n")
                        break
                    elif inp_operation == "0":
                        print("Bye!")
                        exit()
            else:
                print("Wrong card number or PIN! \n")
        elif inp_choice == "0":
            print("Bye!")
            exit()
        else:
            print("There no option like this\n")




if __name__ == "__main__":
    main()