import fitz 
import os 
import math
import io 
from PIL import Image
import genanki
media_files = []
"""def is_number(s):
    if isinstance(s, str):
        if "." in s:
            try:
                float(s)
                return True
 A           except: 
                return False

    return False """
def clean_text(word):
    word = word.replace('\n','').replace('\xa0',' ').replace('\t',' ').replace('\r','')
    word = word.strip()
    return word
"""def is_caca(word):
    word = clean_text(word)
    if word.endswith('.')== False and word.endswith(',') == False : 
        return (False,False) 
    
    parts = word[:-1].replace(',','.').split('.')
    if len(parts)==2 and all(part.isdigit() for part in parts):
        return True,word.replace(',','.')
    return (False,False)""" 
def is_number(word):
    word = clean_text(word)
    #check last character is a dot or comma
    
    if word.endswith('.')== False and word.endswith(',') == False : 
        return False 
    parts = word[:-1].replace(',','.').split('.')
    if   len(parts)==2 and all(part.isdigit() for part in parts):
        return True,word.replace(',','.')
    return False 
def extract_pdf_text(file_path):
    # Open the PDF file
    doc = fitz.open(file_path)
    
    # Extract text from all pages
    text = ''
    for page_num in range(19):
        page = doc.load_page(page_num)  # Load each page
        text += page.get_text("text")  # Extract text (as plain text)
    
    return text
def order(number):
    # Remove the trailing dot, then split into whole and decimal parts
    number = number.replace(',','.')
    number = number.rstrip(".")
    whole, decimal = number.split(".")
    return int(whole), int(decimal) 


def partition(array):
    A = array[:]  # Make a copy of the array to avoid modifying the original
    P = []        # To store the partitions
    M = []        # To store current partition

    while len(A) != 0:
        # Process the last element
        current = A.pop()
        s1 = current.find(".")
        whole1, decimal1 = current[:s1], current[s1+1:-1]

        if len(A) == 0:
            # If it's the last element, add it to the current partition
            M.append(current)
            P.append(M)
            break

       # Check the second-to-last element
        next_element = A[-1]
        s2 = next_element.find(".")
        whole2, decimal2 = next_element[:s2], next_element[s2+1:-1]

        # Compare the whole parts
        if whole1 == whole2:
            M.append(current)  # Add to current partition
        else:
            M.append(current)
            P.append(M)        # Add current partition to P
            M = []             # Reset partition

    return P
def sommairewow(pdf_path):
    a = []
    mydict = {}
    N = extract_text_with_position(pdf_path,0,12)[0]
    i = 0 
    for n in range(len(N)):
        mydict[(N[n][4],N[n][3])]    = (is_number(N[n][5])[1], N[n][3]-N[n-1][3])
        a.append(is_number(N[n][5])[1])
    return sorted(a,key=order),mydict
def sommaire(dictt):
    M = [dictt[key] for key in dictt.keys()]
    L = []
    for k in range(len(M)):
        if 30<M[k][1]<60 :# todo: this range has to be figured automatically btw idk how still anyway 
            L.append(M[k-1][0])
    return L + [M[-1][0]]
def cleansommairewowimsosickk(array):
    M = []
    for L in array:
        
        s = L[-1].find('.')
        M.append([len(L), L[0][s+1:-1]])  
        
    return M 
def extract_text_with_position(pdf_path,start,end):
    doc = fitz.open(pdf_path)
    N = []
    S = []
    B = []
    for page_num in range(start,end):
        page = doc[page_num]
        # extract text and position 
        text_instances = page.get_text("words")

        #print(f"Page {page_num +1}:")
        for inst in text_instances[1:]:
            x0,y0,x1,y1,word,block_no,line_no,word_no = inst
            word_cleaned = clean_text(word)
            if is_number(word_cleaned):
                #if  M!= [] and M[-1][5]==0:
                #M.pop()i 
                # print(f"Text: {word_cleaned}, Positon: (x0 ={x0}, y0 = {y0}, x1 = {x1}, y1 = {y1})")
                x = 0 
                
                N.append([x0,y0,x1,y1,page_num,word_cleaned])
                B.append((word_cleaned,x1))
                
            elif "Solu" in word:
                #print(f"Text: {word}, Positon: (x0={x0}, y0={y0}, x1={x1}, y1 ={y1},exo = {N[-1][5]})")
                S.append([N[-1],[x0,y0,x1,y1,page_num,word_cleaned]])
    return N,S,B 
def anki(pdf_path, start, end):
    """
    Creates an Anki-ready PDF with each problem followed by its solution.
    
    Args:
        pdf_path (str): Path to the input PDF
        start (int): Starting page number
        end (int): Ending page number
    """
    front = []
    back = []
    doc = fitz.open(pdf_path)
    S = extract_text_with_position(pdf_path, start, end)[1]
    output_doc = fitz.open()
 
    for k in range(len(S)-1):  # Iterate until second-to-last item
        front = []
        back = []
        # ok premier bug fixed letsgooo :D 
        """
        BUGS/FEATURES TO FIX: parts when it gives bad crops aka for example when it's in the enpage 

        """

        # Get current problem/solution and next problem coordinates
        current_problem = S[k][0]      # Current problem coords
        current_solution = S[k][1]     # Current solution coords
        next_problem = S[k+1][0]       # Next problem coordinates (where current solution ends)
        
        # ----- Handle Problem Section -----
        problem_page = doc[current_problem[4]]
        problem_page_copy = output_doc.new_page(
            width=problem_page.rect.width,
            height=problem_page.rect.height
        )
        
        # If problem and its solution start are on same page
        if current_problem[4] == current_solution[4]:
            crop_rect = fitz.Rect(0, current_problem[1], problem_page.rect.width, current_solution[1])
            front.append(cimage(pdf_path,crop_rect,current_problem[4]))
        else:
            # Copy until end of page
            crop_rect = fitz.Rect(0, current_problem[1], 
                                problem_page.rect.width, 
                                problem_page.rect.height)
            front.append(cimage(pdf_path,crop_rect,current_problem[4]))
        problem_page_copy.show_pdf_page(
            problem_page_copy.rect,
            doc,
            current_problem[4],
            clip=crop_rect
        )
        
        # If problem spans multiple pages, copy intermediate pages
        if current_problem[4] != current_solution[4]:
            for page_num in range(current_problem[4] + 1, current_solution[4]):
                int_page = doc[page_num]
                int_page_copy = output_doc.new_page(
                    width=int_page.rect.width,
                    height=int_page.rect.height
                )
                front.append(cimage(pdf_path,fitz.Rect(0,0, int_page.rect.width, int_page.rect.height),page_num))
                int_page_copy.show_pdf_page(
                    int_page_copy.rect,
                    doc,
                    page_num
                )
        
        # ----- Handle Solution Section -----
        solution_start_page = doc[current_solution[4]]
        solution_page_copy = output_doc.new_page(
            width=solution_start_page.rect.width,
            height=solution_start_page.rect.height
        )
        
        # If solution and next problem are on same page
        if current_solution[4] == next_problem[4]:
            crop_rect = fitz.Rect(0, current_solution[1],
                                solution_start_page.rect.width,
                                next_problem[1])
            back.append(cimage(pdf_path,crop_rect,current_solution[4]))
        else:
            # Copy from solution start to end of page
            crop_rect = fitz.Rect(0, current_solution[1],
                                solution_start_page.rect.width,
                                solution_start_page.rect.height)
                                
            back.append(cimage(pdf_path,crop_rect,current_solution[4]))
        solution_page_copy.show_pdf_page(
            solution_page_copy.rect,
            doc,
            current_solution[4],
            clip=crop_rect
        )
        
        # If solution spans multiple pages, copy until next problem
        if current_solution[4] != next_problem[4]:
            for page_num in range(current_solution[4] + 1, next_problem[4]):
                int_page = doc[page_num]
                int_page_copy = output_doc.new_page(
                    width=int_page.rect.width,
                    height=int_page.rect.height
                )
                back.append(cimage(pdf_path, fitz.Rect(0,0,int_page.rect.width,int_page.rect.height),page_num))
                int_page_copy.show_pdf_page(
                    int_page_copy.rect,
                    doc,
                    page_num
                )
            
            # Handle last page of solution up to next problem
            if page_num + 1 == next_problem[4]:
                last_sol_page = doc[next_problem[4]]
                last_sol_copy = output_doc.new_page(
                    width=last_sol_page.rect.width,
                    height=last_sol_page.rect.height
                )
                crop_rect = fitz.Rect(0, 0,last_sol_page.rect.width,next_problem[1])
                back.append(cimage(pdf_path,crop_rect,next_problem[4]))
                last_sol_copy.show_pdf_page(
                    last_sol_copy.rect,doc,
                    next_problem[4],
                    clip=crop_rect
                )
        add_card(front,back)

    # Handle the last problem-solution pair
    last_pair = S[-1]
    last_problem = last_pair[0]
    last_solution = last_pair[1]
    
    # Add last problem
    last_prob_page = doc[last_problem[4]]
    last_prob_copy = output_doc.new_page(width=last_prob_page.rect.width,height=last_prob_page.rect.height)
    
    crop_rect = fitz.Rect(0, last_problem[1],last_prob_page.rect.width,last_solution[1])
    last_prob_copy.show_pdf_page(last_prob_copy.rect,doc,last_problem[4],clip=crop_rect)
    
    # Add last solution (copy until end of document)
    last_sol_page = doc[last_solution[4]]
    last_sol_copy = output_doc.new_page(width=last_sol_page.rect.width,height=last_sol_page.rect.height)
    crop_rect = fitz.Rect(0, last_solution[1],last_sol_page.rect.width,last_sol_page.rect.height)
    last_sol_copy.show_pdf_page(last_sol_copy.rect,doc,last_solution[4],clip=crop_rect
    )
    output_doc.save("/home/adalovescoffee/anki.pdf")
    save_deck()
    output_doc.close()
    doc.close()
################################################
#deck shenanigans?
deck_id = 1256498700
deck_name = "math problems test 4 :D "
deck = genanki.Deck(deck_id, deck_name)
pdf_path = "/home/adalovescoffee/Documents/out.pdf"
ordre,dictt = sommairewow(pdf_path)
def cimage(pdf_path, rect, page_number):
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_number)
    pix = page.get_pixmap(clip=rect)
    img_data = pix.pil_tobytes("png")
    image = Image.open(io.BytesIO(img_data))
    image_filename = f'extracted_area_{page_number}_{rect.x0}_{rect.y0}.png'
    image.save(image_filename)
    #
    media_files.append(image_filename)
    
    return image_filename
def add_card(front_images, back_images, front_text='', back_text=''):
    # Concatenate image tags for front and back
    front_field = f'{front_text}<br>' + ''.join([f'<img src="{img}"><br>' for img in front_images])
    back_field = f'{back_text}<br>' + ''.join([f'<img src="{img}"><br>' for img in back_images])
    
    # Create the note
    note = genanki.Note(
        model=genanki.BASIC_MODEL,
        fields=[front_field, back_field]
    )
    
    # Add note to the deck
    deck.add_note(note)

# Function to save the deck as an .apkg file
def save_deck():
    package = genanki.Package(deck)
    package.media_files = media_files 
    package.write_to_file(f'{deck_name}.apkg')


#print(ordre,dictt
#dictt = sorted(dictt)
#print(dictt)

#print(sommaire(dictt))
#partition(ordre)
print(partition(ordre))
print(cleansommairewowimsosickk(partition(ordre)))

#print(is_number("2.2,"))

#A = extract_text_with_position(pdf_path,15,313)
#print(A[1])

#anki(pdf_path,15,doc.page_count)
raw_text = extract_pdf_text(pdf_path)
#print(repr(raw_text))


#####################################################################
"""TODO: 
--have an llm see first pages, give regex that detects problem/solutions positions to crop ez 
--make randomodoro 
--make website/platform (probably in django) (rip me)
--lean proof checker (?maybe)
--streak thing 
--give problems based on goals (llm etc blablabla)
--idk we'll see 
"""
