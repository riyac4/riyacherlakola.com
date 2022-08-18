import sys
import os
import datetime
import glob
import shutil
from PIL import Image


# Function I wrote to convert ./data/2022-06-22.md into Jun 22, 2022
def date_converter(item):
    filename = os.path.basename(item)
    filedate = filename.split(".")
    actdate = filedate[0]
    datelist = actdate.split("-")
    nicedate = datetime.datetime(
        int(datelist[0]), int(datelist[1]), int(datelist[2]))
    finaldate = nicedate.strftime("%b %d, %Y")
    return finaldate


def get_filename(item):
    filename = os.path.basename(item)
    filedate = filename.split(".")
    actdate = filedate[0]
    return actdate + ".html"

# This should just return an array of all the lines
def read_lines(item):
    blog_post = open(item, "r")
    all_lines = blog_post.readlines()
    blog_post.close()
    # print(all_lines)
    return all_lines


def get_title(lines):
    first_line = lines[0]
    return first_line[2:]


def get_thumbnail(lines):
    for line in lines:
        if (line[0] == "!"):
            return line[4:-2]
    return ""


# Trims paragraph down to desired length of 4 lines and will chop of at space
def trim_para(my_string):
    trim = my_string[:340]
    # return trim
    return trim[0:trim.rfind(" ")] + "..."

# Gets the summary which will be two lines below the ## and will return the nice string
def get_summary(lines):
    for i, line in enumerate(lines):
        if(line[0:2] == "##"):
            paragraph = lines[i + 2]
            para_arr = paragraph.split()
            chars = format_summary(para_arr)
            # if (chars[-1] != " "):
            return trim_para(chars)
    return ""

# Formats the array into a pargraph
def format_summary(para_arr):
    summary = ""
    for word in para_arr:
        summary += word
        summary += " "

    return summary + "..."


# def get_body(lines):
#     body_text = ""
#     index = 0
#     for i, line in enumerate(lines):
#         if(line[0:2] == "##"):
#             index = i
#             break
#     after_lines = lines[index:]
#     for i, line in enumerate(after_lines):
#         body_text += after_lines[i]
#     return body_text
def convert(lines):
    index = 0
    for i, line in enumerate(lines):
        if(line[0:2] == "##"):
            index = i
            break
    after_lines = lines[index:]
    body = ""
    html = ""
    new_array_lines = []
    for before_strip in after_lines:
        if (before_strip != '\n'):
            after_strip_lines = before_strip.strip()  
            new_array_lines.append(after_strip_lines)
        else:
            new_array_lines.append(before_strip)
    #print(new_array_lines)
    for line in new_array_lines:
        if (line[0:2] == "##"):
            html = "<h2>" + line[3:] + "</h2>"
            body += html
        elif (line[0] == "!"):
            html = "<img src='{{IMG}}' alt='{{IMG}}'>"
            html_img = html.replace("{{IMG}}", line[4:-1])
            body += html_img
        elif (line[0] == "\n"):
            body = body
        elif (line[0:2] == "!["):
            print("This is a img")
        elif (line.find("[") > -1):
            body += link_convert(line)
        else:
            html = "<p>" + line + "</p>"
            body += html
    return body



def link_convert(line):
    html = "<a href='{{URL}}'>{{NAME}}</a>"
    link_line = 0
    first_bracket = 0
    sec_bracket = 0
    first_paren = 0
    sec_paren = 0
    for i, char in enumerate(line):
        if (char == "["):
            first_bracket = i
        if (char == "]"):
            sec_bracket = i
        if (char == "("):
            first_paren = i
        if (char == ")"):
            sec_paren = i + 1
    link = line[first_bracket:sec_paren]
    name = line[first_bracket + 1:sec_bracket]
    url = line[first_paren + 1:sec_paren - 1]
    # print("link--> " + link)
    # print("url--> " + url)
    # print("name--> " + name)
    new_line = line.replace(link, "{{LINK}}")
    a_tag = html.replace("{{URL}}", url).replace("{{NAME}}", name)
    final_line = new_line.replace("{{LINK}}", a_tag)
    # print(final_line)
    return "<p>" + final_line + "</p>"
# Gets an array of tags


def get_tags(lines):
    for line in lines:
        if (line[0:20] == "[comment]: <> (tags:"):
            tag_str = line[20:-2]
            tag_list = tag_str.split(",")
            return tag_list
    return ""

def copy_images():
	src = './data/blog-images'
	dst = './dist/articles/blog-images/'
	img_list = glob.glob(src + '/*.*')
	for img_path in img_list:
		print('img_path is ...' + img_path)
		dst_path = dst + os.path.basename(img_path)
		if (not os.path.exists(dst_path)):
			if (img_path.lower().find('.jpg') > 0):
				print('compressing .... ' + img_path + ' to ' + dst)
				img_obj = Image.open(img_path)
				if (img_obj.size[0] > 1024):
					print('even resizing 1024 max width...')
					img_obj = img_obj.resize( (1024, int(img_obj.size[1] * 1024 / img_obj.size[0])) )
				img_obj.save(dst_path, "JPEG", optimize=True, quality=80)
			else:
				print('Copying .... ' + img_path + ' to ' + dst)
				shutil.copy(img_path, dst)
		else:
			print(dst_path + ' exists... skipping.')


# Main build function. Take source file, merge them with templates,
# and then export them into dist folder
def generate():
	# Opening the og blog template to read it
	f = open("./assets/templates/blog.html", "r")
	blog = f.read()
	# Always make sure u close the flie once done reading or writing
	f.close()
	det = open("./assets/templates/details.html", "r")
	details = det.read()
	det.close()
	# The html for the card format
	card = '''
	 <div class="card shadow mb-4">
				<div class="row">
					<div class="col-md-4" >
						<img src="<!--{{IMG}}-->"  style="  width: 100%;
				  height: 32vh;
					object-fit: cover;"alt="<!--{{IMG}}-->">
					 </div>
					<div class="col-md-8 py-0 d-flex flex-column position-static" >
						<a href="./articles/<!--{{FILENAME}}-->" class="text-decoration-none"><h2 class="card-title pt-2 mt-1 mb-0"><!--{{TITLE}}--></h2></a>
						<div class=" text-muted my-1"><!--{{DATE}}--></div>
						<p class="mb-auto card-text" style="padding-right: 10px;"><!--{{SUM}}--></p>
						<div class ="card-footer px-0" style="background: transparent; border-top:0px; border-left: 0px;"> 
						<!--{{BUTTON}}-->
						</div>
					</div>
				</div>
			</div>
		'''
	tag_button = '''<button type="button" class=" flex btn btn-outline-secondary btn-sm my-1"><!--{{TAG}}--></button>'''

	blog_section = '''<div class="row d-flex justify-content-center">
		  <div class="col-md-9">
		  <article class="card mb-4">
			<header class="card-header text-center">
			  <h1 class="card-title"><!--{{TITLE}}--></h1>
			  <div class="text-muted mb-1"><!--{{DATE}}--></div>
		   <!--{{BUTTON}}-->
			</header>
			<a href="post-image.html">
			  <img class="card-img" src="<!--{{IMG}}-->" alt="" />
			</a>
			<div class="card-body">
			  <p>
				<!--{{BODY}}-->
			  </p> 
		  </article>
		  <a href="#">Previous</a>
		  <a href="#">Next</a>
		</div> '''
	# Using glob to get all the md files in the data folder
	list = sorted(glob.glob("./data/*.md"))
	list.reverse()

	# The storage of the concatination
	all_cards = ""

	# print(list)
	# A for loop to loop through the items in list (all the blog-posts.md) and replace html comments with parts of md files
	for item in list:
		filename = get_filename(item)
		finaldate = date_converter(item)
		lines = read_lines(item)
		# print(lines)
		title = get_title(lines)
		img = get_thumbnail(lines)
		img_parent = img.replace('./', './articles/')
		summary = get_summary(lines)
		body_text = convert(lines)
		tag_list = get_tags(lines)
		tags = ""
		for tag in tag_list:
			tag_all = tag_button.replace("<!--{{TAG}}-->", tag)
			tags += tag_all
			tags += '\n'
		# print(tags)
		card_chunk = card.replace(
			"<!--{{DATE}}-->", finaldate).replace("<!--{{TITLE}}-->", title).replace("<!--{{IMG}}-->", img_parent).replace("<!--{{SUM}}-->", summary).replace("<!--{{BUTTON}}-->", tags).replace("<!--{{FILENAME}}-->", filename)
		all_cards += card_chunk
		detail_chunk = blog_section.replace(
			"<!--{{DATE}}-->", finaldate).replace("<!--{{TITLE}}-->", title).replace("<!--{{IMG}}-->", img).replace("<!--{{BODY}}-->", body_text).replace("<!--{{BUTTON}}-->", tags).replace("<!--{{FILENAME}}-->", filename)
		output_article = details.replace("<!-- {{BLOG SECTION}} -->", detail_chunk)
		fwb = open("./dist/articles/" + filename, "w")
		fwb.write(output_article)
		fwb.close()
	output_blog = blog.replace("<!-- {{CARD}} -->", all_cards)

	# Write the file to a dist folder, rebuilds blog.html page with input from the data blog posts
	fw = open("./dist/blog.html", "w")
	fw.write(output_blog)
	fw.close()

	# Copy Images
	copy_images()

#Tests!!!
if len(sys.argv) == 1:
	generate() 
	print("site has been generated in dist folder")
elif len(sys.argv) > 1 and sys.argv[1] == '--help':
	print("==============================================")
	print("[Static Site Builder Usage]")
	print("python site-builder.py [--help|--test]")
	print("----------------------------------------------")
	print("[Examples]")
	print("python site-builder.py")
	print("python site-builder.py --help")
	print("python site-builder.py --test")
	print("==============================================")
elif len(sys.argv) > 1 and sys.argv[1] == '--test':
	test_space = ['       ## This is a test line.         ']
	output_space = '<h2>This is a test line.</h2>'
	test_space_two = ['     ## My Trip To Chicago\n     ', '\n', '   ![](../images/chi.jpg)\n', '\n']
	output_space_two = "<h2>My Trip To Chicago</h2><img src='../images/chi.jp' alt='../images/chi.jp'>"
	test_space_three = ['     ## My Trip To Chicago\n     ', '\n', '\n', '\n', '\n']
	output_space_three = "<h2>My Trip To Chicago</h2>"
	print("test one")
	print(convert(test_space) == output_space)
	print("test two")
	print(convert(test_space_two) == output_space_two)
	print("test three")
	print(convert(test_space_three) == output_space_three)
