cd roles/sf_config/files/src-demo-java

git init
git remote add origin ssh://git@git.kitstartup.ovh:8022/demo/kitdemo.git
#git remote add origin https://git.kitstartup.ovh/demo/kitdemo.git
git add .
git commit -a -m "first commit message"
git push -u origin master
#git push --set-upstream https://git.kitstartup.ovh/demo/kitdemo.git master
