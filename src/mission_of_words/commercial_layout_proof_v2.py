"""Little Lampkeepers - zero-cost commercial layout proof v2.

No GPT2, no paid calls. This is a full 48-page visual architecture proof.
Search & Find is now scene-first: a complete illustrated scene is drawn first,
then eight deterministic target objects are integrated into that scene. The
answer key reuses the exact same target coordinates.
"""

from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib.colors import Color, white
from reportlab.pdfgen import canvas

from mission_of_words import art
from mission_of_words.bible import bind_mission_record
from mission_of_words.book_manifest import load_book_record, load_mission_records
from mission_of_words.layout import PAGE_H, PAGE_W, content_box
from mission_of_words.maze import generate_maze
from mission_of_words.render import contact_sheet_grid, render_pdf_pages
from mission_of_words.scenes import draw_coloring_scene
from mission_of_words.templates import draw_maze_grid

OUT = Path("output/commercial_layout_v2")
PDF = OUT / "LittleLampkeepers_48_Page_Commercial_Layout_Proof_V2.pdf"
REPORT = OUT / "layout_report.json"
PREVIEWS = OUT / "previews"

INK = Color(0.07, 0.07, 0.07)


def panel(c, box, radius=14, width=1.5):
    l, b, r, t = box
    c.setStrokeColor(INK); c.setFillColor(white); c.setLineWidth(width)
    c.roundRect(l, b, r-l, t-b, radius, fill=1, stroke=1)


def wrap(c, text, font, size, max_width):
    words = str(text or "").split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if not cur or c.stringWidth(trial, font, size) <= max_width:
            cur = trial
        else:
            lines.append(cur); cur = word
    if cur: lines.append(cur)
    return lines


def draw_lines(c, lines, x, y, font="Helvetica", size=11, leading=14, centered=False, width=0):
    c.setFillColor(INK); c.setFont(font, size)
    yy = y
    for line in lines:
        if centered: c.drawCentredString(x + width/2, yy, line)
        else: c.drawString(x, yy, line)
        yy -= leading
    return yy


def footer(c, page, left, bottom, right):
    c.setFillColor(INK); c.setFont("Helvetica-Bold", 9)
    c.drawRightString(right, bottom-18, str(page))


def header(c, mission, page, activity, title=None):
    left, bottom, right, top = content_box(page)
    width = right-left
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(left, top-2, f"MISSION {mission['sequence']}  |  {activity.upper()}")
    c.setFont("Helvetica-Oblique", 10.5)
    c.drawRightString(right, top-2, mission["scripture_reference"])
    display = title or mission["title"]
    title_lines = wrap(c, display, "Helvetica-Bold", 25, width*0.80)
    y = top-34
    y = draw_lines(c, title_lines, left, y, font="Helvetica-Bold", size=25, leading=28)
    return left, bottom, right, y-4


def instruction(c, text, left, y, width, size=11.5):
    return draw_lines(c, wrap(c, text, "Helvetica", size, width), left, y, size=size, leading=size+3)


def target_icon(c, name, x, y, scale=1.0):
    key = str(name).lower()
    if key == "lantern": art.draw_lantern(c, x-9*scale, y-12*scale, 24*scale)
    elif key == "pumpkin": art.draw_pumpkin(c, x, y, 17*scale)
    elif key == "apple": art.draw_apple(c, x, y, 15*scale)
    elif key == "leaf": art.draw_leaf(c, x-7*scale, y-8*scale, 18*scale)
    elif key == "acorn": art.draw_acorn(c, x-7*scale, y-8*scale, 16*scale)
    elif key == "scarf": art.draw_scarf(c, x-7*scale, y-8*scale, 18*scale)
    elif key == "basket": art.draw_basket(c, x-9*scale, y-9*scale, 20*scale)
    elif key == "bible": art.draw_bible(c, x-9*scale, y-11*scale, 20*scale)
    else: art.draw_star(c, x, y, 8*scale)


def title_page(c, book, page):
    l,b,r,t = content_box(page)
    c.setFillColor(INK); c.setFont("Helvetica-Bold", 31)
    c.drawCentredString((l+r)/2, t-32, "Little Lampkeepers")
    c.setFont("Helvetica-Bold", 24); c.drawCentredString((l+r)/2, t-68, "Shine Your Light This Fall")
    c.setFont("Helvetica", 12.5); c.drawCentredString((l+r)/2, t-94, "A Christian Fall Activity Book for Kids Ages 5-8")
    draw_coloring_scene(c, "mission_01", (l+8,b+92,r-8,t-128))
    panel(c, (l+42,b+24,r-42,b+70), 20, 1.8)
    c.setFont("Helvetica-Bold", 12); c.drawCentredString((l+r)/2,b+43,"COLOR  |  SEARCH  |  MAZE  |  THINK  |  PRAY  |  GROW")
    footer(c,page,l,b,r)


def welcome_page(c,page):
    l,b,r,t=content_box(page)
    c.setFillColor(INK); c.setFont("Helvetica-Bold",26); c.drawCentredString((l+r)/2,t-24,"Welcome, Little Lampkeeper!")
    intro="Every mission connects a Bible truth to something you can color, solve, notice, choose, or pray about."
    draw_lines(c,wrap(c,intro,"Helvetica",13,r-l-50),l+25,t-60,size=13,leading=18,centered=True,width=r-l-50)
    cards=[("1","READ","Read the Bible truth together."),("2","PLAY","Complete the activity."),("3","THINK","Talk about one real-life choice."),("4","DO","Put faith into action this week.")]
    y=t-140
    for n,h,body in cards:
        panel(c,(l+28,y-74,r-28,y),16,1.6)
        c.setFont("Helvetica-Bold",22); c.drawCentredString(l+58,y-45,n)
        c.setFont("Helvetica-Bold",13); c.drawString(l+92,y-28,h)
        c.setFont("Helvetica",11.5); c.drawString(l+92,y-49,body)
        y-=90
    art.draw_heart(c,(l+r)/2,b+92,20)
    c.setFont("Helvetica-Bold",15); c.drawCentredString((l+r)/2,b+48,"Small hearts can make a bright difference.")
    footer(c,page,l,b,r)


def contents_page(c,missions,page):
    l,b,r,t=content_box(page)
    c.setFillColor(INK); c.setFont("Helvetica-Bold",26); c.drawCentredString((l+r)/2,t-24,"Eight Fall Faith Missions")
    y=t-78
    for m in missions:
        start=int(m["global_page_start"]); panel(c,(l+12,y-54,r-12,y),12,1.2)
        c.setFont("Helvetica-Bold",12); c.drawString(l+30,y-23,f"Mission {m['sequence']}")
        c.setFont("Helvetica-Bold",14); c.drawString(l+120,y-23,m["title"])
        c.setFont("Helvetica",10); c.drawRightString(r-30,y-23,f"pages {start}-{start+3}")
        c.setFont("Helvetica-Oblique",9.5); c.drawString(l+120,y-41,m["scripture_reference"])
        y-=64
    footer(c,page,l,b,r)


def parent_page(c,page):
    l,b,r,t=content_box(page)
    c.setFillColor(INK); c.setFont("Helvetica-Bold",24); c.drawCentredString((l+r)/2,t-24,"For Parents and Grown-Ups")
    text="Use each four-page mission as a short screen-free faith moment. Read the Bible reference, let your child explore the activity, then use the final page as a conversation and prayer prompt."
    draw_lines(c,wrap(c,text,"Helvetica",12.5,r-l-70),l+35,t-70,size=12.5,leading=17,centered=True,width=r-l-70)
    notes=[("Bible-first","Every mission connects the activity to a specific Bible truth."),("Kid-sized","Directions are short and pages are designed for ages 5-8."),("Screen-free","Pencils and crayons are ideal; use scrap paper behind marker pages."),("Talk together","There is no single perfect answer on the Faith in Action page.")]
    y=t-150
    for h,body in notes:
        panel(c,(l+28,y-74,r-28,y),15,1.4)
        c.setFont("Helvetica-Bold",13); c.drawString(l+48,y-25,h)
        draw_lines(c,wrap(c,body,"Helvetica",10.5,r-l-190),l+150,y-25,size=10.5,leading=14)
        y-=90
    footer(c,page,l,b,r)


def coloring_page(c,m,canon,page):
    l,b,r,y=header(c,m,page,"Color and Reflect")
    verse=canon.get("child_paraphrase") or canon.get("source_text") or ""
    y=instruction(c,verse,l,y,r-l,11.5)-8
    think_h=74
    draw_coloring_scene(c,m["id"],(l,b+think_h+16,r,y))
    panel(c,(l,b,r,b+think_h),16,1.6)
    c.setFont("Helvetica-Bold",11.5); c.drawString(l+16,b+48,"THINK ABOUT IT")
    prompt=m["pages"][3].get("drawing_prompt") or m["pages"][0]["bible_connection"]
    draw_lines(c,wrap(c,prompt,"Helvetica",11,r-l-34)[:2],l+16,b+28,size=11,leading=14)
    footer(c,page,l,b,r)


def search_scene(c,m,scene,target_rows,answer=False):
    l,b,r,t=scene; w=r-l; h=t-b
    draw_coloring_scene(c,m["id"],(l+5,b+5,r-5,t-5))
    coords=[]
    for idx,row in enumerate(target_rows, start=1):
        # Target records use top-origin ratios in the production compositor.
        x=l+w*(0.06+float(row["x"])*0.88)
        y=t-h*(0.08+float(row["y"])*0.82)
        target_icon(c,row["name"],x,y,0.72)
        coords.append((row["name"],x,y))
        if answer:
            c.setLineWidth(1.6); c.circle(x,y,16,fill=0,stroke=1)
            c.setFont("Helvetica-Bold",8.5); c.drawCentredString(x,y+19,str(idx))
    return coords


def search_page(c,m,canon,page,cache):
    spec=m["pages"][1]
    l,b,r,y=header(c,m,page,"Search and Find",spec["title"])
    y=instruction(c,spec["child_instruction"],l,y,r-l,11.5)-6
    legend_h=86; legend=(l,y-legend_h,r,y); panel(c,legend,14,1.4)
    rows=spec["targets"]; col_w=(r-l-24)/4
    for i,row in enumerate(rows):
        col=i%4; rr=i//4; x=l+16+col*col_w; yy=y-25-rr*35
        target_icon(c,row["name"],x+8,yy+6,0.85)
        c.setFont("Helvetica-Bold",8.8); c.drawString(x+27,yy+2,row["name"].title())
    scene=(l,b,r,legend[1]-10); panel(c,scene,14,1.5)
    coords=search_scene(c,m,scene,rows,answer=False)
    cache[m["id"]]={"targets":rows,"coords":coords}
    footer(c,page,l,b,r)


def maze_decor(c,mission_id,box):
    l,b,r,t=box; w=r-l; h=t-b
    art.draw_cloud(c,l+w*0.03,t-38,w*0.16); art.draw_cloud(c,r-w*0.22,t-46,w*0.15)
    art.draw_ground(c,l,b,w,h*0.16)
    if mission_id in {"mission_01","mission_06"}:
        art.draw_church(c,l+4,t-h*0.28,w*0.17,h*0.20); art.draw_string_lights(c,l+w*0.72,t-h*0.10,r-12,t-h*0.04,bulbs=5)
    elif mission_id in {"mission_02","mission_03"}:
        art.draw_tree(c,l+4,b+8,w*0.16,h*0.30); art.draw_barn(c,r-w*0.22,t-h*0.27,w*0.20,h*0.18)
    elif mission_id=="mission_04":
        art.draw_tree(c,l+4,b+8,w*0.16,h*0.34); art.draw_porch(c,r-w*0.22,t-h*0.28,w*0.20,h*0.20,lit=True)
    elif mission_id=="mission_05":
        art.draw_basket(c,l+8,b+12,34); art.draw_porch(c,r-w*0.22,t-h*0.28,w*0.20,h*0.20,lit=False)
    elif mission_id=="mission_07":
        art.draw_tree(c,l+4,b+8,w*0.16,h*0.32); art.draw_deer(c,r-w*0.20,b+14,w*0.14,h*0.14)
    else:
        art.draw_table(c,l+8,b+10,w*0.16,h*0.09); art.draw_window(c,r-w*0.18,t-h*0.22,w*0.14,h*0.12)


def maze_page(c,m,canon,page,cache):
    spec=m["pages"][2]
    l,b,r,y=header(c,m,page,"Mission Maze",spec["title"])
    y=instruction(c,spec["child_instruction"],l,y,r-l,11.5)-4
    scene=(l,b,r,y); maze_decor(c,m["id"],scene)
    rows,cols=spec["grid"]; maze=generate_maze(rows=rows,cols=cols,seed=int(spec["seed"])); cache.setdefault(m["id"],{})["maze"]=maze
    sx,sy,sr,st=scene; w=sr-sx; h=st-sy
    window=(sx+w*0.13,sy+h*0.14,sr-w*0.13,st-h*0.14); panel(c,window,18,2.0)
    pad=18; cell=min((window[2]-window[0]-2*pad)/cols,(window[3]-window[1]-2*pad)/rows)
    x0=window[0]+(window[2]-window[0]-cols*cell)/2; y0=window[1]+(window[3]-window[1]-rows*cell)/2
    draw_maze_grid(c,maze,x0=x0,y0=y0,cell=cell,answer_key=False)
    c.setFont("Helvetica-Bold",9.5); c.drawString(window[0]+10,window[3]+5,"START"); c.drawRightString(window[2]-10,window[1]-13,"FINISH")
    footer(c,page,l,b,r)


def choice_icon(c,icon,x,y):
    key=str(icon).lower()
    if key in {"help","share","kind","friend","include","family","people","hands"}: art.draw_heart(c,x,y,10)
    elif key in {"leaf","plant","bird"}: art.draw_leaf(c,x-6,y-8,16)
    elif key in {"apple","meal","bread"}: art.draw_apple(c,x,y,13)
    else: art.draw_star(c,x,y,8)


def faith_page(c,m,canon,page):
    spec=m["pages"][3]
    l,b,r,y=header(c,m,page,"Faith in Action",spec["title"])
    truth=canon.get("child_paraphrase") or spec["bible_connection"]
    truth_h=62; panel(c,(l,y-truth_h,r,y),16,1.4)
    c.setFont("Helvetica-Bold",10.5); c.drawString(l+14,y-18,"BIBLE TRUTH")
    draw_lines(c,wrap(c,truth,"Helvetica",10.5,r-l-28)[:2],l+14,y-36,size=10.5,leading=13)
    y-=truth_h+12
    gap=10; card_w=(r-l-gap)/2; card_h=62
    for i,ch in enumerate(spec["choices"]):
        col=i%2; rr=i//2; x=l+col*(card_w+gap); top=y-rr*(card_h+gap); box=(x,top-card_h,x+card_w,top); panel(c,box,14,1.3)
        c.rect(x+12,top-27,13,13,fill=0,stroke=1); choice_icon(c,ch.get("icon",""),x+card_w-24,top-29)
        draw_lines(c,wrap(c,ch["label"],"Helvetica-Bold",10.5,card_w-70)[:2],x+34,top-22,font="Helvetica-Bold",size=10.5,leading=13)
    y-=2*(card_h+gap)+8
    c.setFont("Helvetica-Bold",11.5); c.drawString(l,y,spec["drawing_prompt"]); y-=12
    prayer_h=52; draw_box=(l,b+prayer_h+10,r,y); panel(c,draw_box,18,1.7)
    # Decorative frame marks the drawing area as part of the page rather than a blank worksheet rectangle.
    art.draw_lantern(c,(l+r)/2-26,(draw_box[1]+draw_box[3])/2-35,70)
    art.draw_leaf(c,l+16,draw_box[3]-30,22); art.draw_leaf(c,r-34,draw_box[1]+18,22)
    c.setFont("Helvetica-Oblique",11); c.drawCentredString((l+r)/2,b+prayer_h+24,"Draw or write your idea here")
    panel(c,(l,b,r,b+prayer_h),14,1.4); c.setFont("Helvetica-Bold",10.5); c.drawString(l+14,b+33,"PRAYER")
    c.setFont("Helvetica",10.5); c.drawString(l+70,b+33,spec["prayer"])
    footer(c,page,l,b,r)


def answer_key(c,m,canon,page,cache):
    l,b,r,t=content_box(page)
    c.setFillColor(INK); c.setFont("Helvetica-Bold",22); c.drawString(l,t-6,f"Mission {m['sequence']} Answer Key")
    c.setFont("Helvetica",10.5); c.drawString(l,t-26,m["title"]); c.setFont("Helvetica-Oblique",9.5); c.drawRightString(r,t-26,m["scripture_reference"])
    split=b+(t-b)*0.51; sbox=(l,split+10,r,t-52); mbox=(l,b,r,split-8); panel(c,sbox,14,1.4); panel(c,mbox,14,1.4)
    c.setFont("Helvetica-Bold",11); c.drawString(sbox[0]+12,sbox[3]-18,"SEARCH AND FIND"); c.drawString(mbox[0]+12,mbox[3]-18,"MAZE SOLUTION")
    scene=(sbox[0]+12,sbox[1]+12,sbox[2]-12,sbox[3]-30); search_scene(c,m,scene,cache[m["id"]]["targets"],answer=True)
    maze=cache[m["id"]]["maze"]; rows,cols=maze.rows,maze.cols; inner=(mbox[0]+34,mbox[1]+28,mbox[2]-34,mbox[3]-34)
    cell=min((inner[2]-inner[0])/cols,(inner[3]-inner[1])/rows); x0=inner[0]+((inner[2]-inner[0])-cols*cell)/2; y0=inner[1]+((inner[3]-inner[1])-rows*cell)/2
    draw_maze_grid(c,maze,x0=x0,y0=y0,cell=cell,answer_key=True)
    footer(c,page,l,b,r)


def journal(c,page):
    l,b,r,t=content_box(page); c.setFillColor(INK); c.setFont("Helvetica-Bold",25); c.drawCentredString((l+r)/2,t-20,"My Gratitude Journal")
    c.setFont("Helvetica",11.5); c.drawCentredString((l+r)/2,t-46,"Today I thank God for...")
    y=t-92
    for _ in range(10): art.draw_heart(c,l+12,y+3,5); c.line(l+34,y,r,y); y-=50
    footer(c,page,l,b,r)


def prayers(c,page):
    l,b,r,t=content_box(page); c.setFillColor(INK); c.setFont("Helvetica-Bold",25); c.drawCentredString((l+r)/2,t-20,"My Prayers")
    c.setFont("Helvetica",11.5); c.drawCentredString((l+r)/2,t-46,"People, places, and things I can pray about")
    y=t-92
    for _ in range(9): c.circle(l+14,y+3,4,fill=0,stroke=1); c.line(l+34,y,r,y); y-=54
    art.draw_cross(c,(l+r)/2-3,b+36,20); footer(c,page,l,b,r)


def certificate(c,page):
    l,b,r,t=content_box(page); panel(c,(l+10,b+10,r-10,t-10),22,2.0)
    c.setFillColor(INK); c.setFont("Helvetica-Bold",28); c.drawCentredString((l+r)/2,t-72,"You Are a Light!")
    c.setFont("Helvetica",13); c.drawCentredString((l+r)/2,t-102,"Certificate of Completion"); art.draw_heart(c,(l+r)/2,t-155,18)
    c.setFont("Helvetica",11.5); c.drawCentredString((l+r)/2,t-205,"This certifies that"); c.line(l+95,t-244,r-95,t-244)
    c.setFont("Helvetica-Bold",12); c.drawCentredString((l+r)/2,t-286,"completed Little Lampkeepers: Shine Your Light This Fall")
    c.setFont("Helvetica",11); c.drawCentredString((l+r)/2,b+110,"Keep shining through kindness, courage, gratitude, sharing, and prayer.")
    c.setFont("Helvetica-Bold",12); c.drawCentredString((l+r)/2,b+62,"Matthew 5:16"); footer(c,page,l,b,r)


def closing(c,page):
    l,b,r,t=content_box(page); c.setFillColor(INK); c.setFont("Helvetica-Bold",29); c.drawCentredString((l+r)/2,t-34,"Keep Shining!")
    draw_coloring_scene(c,"mission_01",(l+10,b+100,r-10,t-82)); panel(c,(l+50,b+22,r-50,b+74),20,1.6)
    c.setFont("Helvetica-Bold",12); c.drawCentredString((l+r)/2,b+48,"FAITH  |  KINDNESS  |  COURAGE  |  GRATITUDE  |  LOVE"); footer(c,page,l,b,r)


def build():
    OUT.mkdir(parents=True,exist_ok=True); PREVIEWS.mkdir(parents=True,exist_ok=True)
    book=load_book_record(); missions=load_mission_records(); canons={m["id"]:bind_mission_record(m) for m in missions}; cache={}
    c=canvas.Canvas(str(PDF),pagesize=(PAGE_W,PAGE_H)); c.setTitle("Little Lampkeepers - Commercial Layout Proof V2")
    title_page(c,book,1); c.showPage(); welcome_page(c,2); c.showPage(); contents_page(c,missions,3); c.showPage(); parent_page(c,4); c.showPage()
    for m in missions:
        start=int(m["global_page_start"]); canon=canons[m["id"]]
        coloring_page(c,m,canon,start); c.showPage(); search_page(c,m,canon,start+1,cache); c.showPage(); maze_page(c,m,canon,start+2,cache); c.showPage(); faith_page(c,m,canon,start+3); c.showPage()
    for m in missions: answer_key(c,m,canons[m["id"]],36+int(m["sequence"]),cache); c.showPage()
    journal(c,45); c.showPage(); prayers(c,46); c.showPage(); certificate(c,47); c.showPage(); closing(c,48); c.showPage(); c.save()
    previews=render_pdf_pages(PDF,PREVIEWS,dpi=130,prefix="page"); contact=PREVIEWS/"contact_sheet.png"; contact_sheet_grid(previews,contact,columns=6)
    contact_sheet_grid(previews[4:20],PREVIEWS/"missions_1_4.png",columns=4); contact_sheet_grid(previews[20:36],PREVIEWS/"missions_5_8.png",columns=4)
    report={"status":"PASS_LAYOUT_PROOF_CREATED" if len(previews)==48 else "FAIL","paid_image_calls":0,"page_count":len(previews),"trim_inches":[8.5,11.0],"brand":"Little Lampkeepers","proof_only":True,"gpt2_allowed":False,"search_and_find":"scene-first vector composition with deterministic integrated targets","pdf":str(PDF),"contact_sheet":str(contact)}
    REPORT.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8"); print(json.dumps(report,indent=2)); return report


if __name__=="__main__": build()
