from django.shortcuts import render, redirect
from .models import Post
import cv2, os, shutil


# Create your views here.
def index(request):
    return render(request, 'main/index.html')


def remove_files(dir_path):
    for (root, directories, files) in os.walk(dir_path):
        for file in files:
            file_path = os.path.join(root, file)

            if os.path.exists(file_path):
                os.remove(file_path)    


def file_exist_check(file_name):
    dir_path = "/content/django-board/media"
    for (root, directories, files) in os.walk(dir_path):
        for file in files:
            if str(file) == file_name:
                return True       
    return False

                


def image_super_resolution():
    print("======================================")
    os.system('python main.py --data_test Demo --scale 4 --pre_train download --test_only --save_results')
    print("======================================")
    
    dir_path = "/content/django-board/EDSR-PyTorch/experiment/test/results-Demo"
    for (root, directories, files) in os.walk(dir_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_name = file_path.split(".")[0]
            file_name = file_name[64:]
            file_name = "x4_" + file_name.split("_")[0]

            sr_img = cv2.imread(file_path)

            cv2.imwrite("/content/django-board/media/" + file_name + ".jpg", sr_img)

    remove_files(dir_path)
    remove_files("/content/django-board/EDSR-PyTorch/test")





def blog(request):
    postlist = Post.objects.all()
    return render(request, 'main/blog.html', {'postlist': postlist})


def posting(request, pk):
    post = Post.objects.get(pk=pk)
    if file_exist_check("x4_" + str(post.mainphoto)):
        print("이미 SR 결과물이 존재합니다.")
    else:
        image_super_resolution()

    return render(request, 'main/posting.html', {'post': post})


def after_save_post(request):
    return render(request, 'main/save_check.html')


def after_delete_post(request):
    return render(request, 'main/delete_check.html')


def new_post(request):
    if request.method == 'POST':
        try:
            new_article = Post.objects.create(
                postname=request.POST['postname'],
                contents=request.POST['contents'],
                mainphoto=request.FILES['mainphoto'],
            )
        except:
            new_article = Post.objects.create(
                postname=request.POST['postname'],
                contents=request.POST['contents'],
            )
        # return redirect('/blog/')

        file_name = str(request.FILES['mainphoto'])

        ori_img = cv2.imread("/content/django-board/media/" + file_name)
        low_img = cv2.resize(ori_img, dsize=(0, 0), fx=0.25, fy=0.25, interpolation=cv2.INTER_CUBIC)

        cv2.imwrite("/content/django-board/low_img_store/" + file_name, low_img)
        cv2.imwrite("/content/django-board/media/" + "low_" + file_name, low_img)
        cv2.imwrite("/content/django-board/EDSR-PyTorch/test/" + file_name, low_img)

        cv2.imwrite("/content/django-board/ori_img_store/" + file_name, ori_img)

        return after_save_post(request)
    return render(request, 'main/new_post.html')


def remove_post(request, pk):
    post = Post.objects.get(pk=pk)
    if request.method == 'POST':
        post.delete()
        # return redirect('/blog/')
        return after_delete_post(request)
    return render(request, 'main/remove_post.html', {'Post': post})


def SR(request):
    image_super_resolution()
    return render(request, 'main/SR_check.html')


def get_dir_size(path='.'):
    total = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path)
    return round(total / (1024*1024), 2)


def admin_page(request):
    low_img_store_capacity = get_dir_size("/content/django-board/low_img_store")
    ori_img_store_capacity = get_dir_size("/content/django-board/ori_img_store")
    saved = ori_img_store_capacity - low_img_store_capacity

    return render(request, 'main/store_check.html', {'low_capacity' : low_img_store_capacity, 'ori_capacity' : ori_img_store_capacity, 'saved' : saved})


def compare(request, pk):
    post = Post.objects.get(pk=pk)
    return render(request, 'main/compare.html', {'post': post})


