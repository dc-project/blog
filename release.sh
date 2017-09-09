#!/bin/bash

set -xe

image_name="projectdc/blog"
gitDescribe=$(git describe --tag|sed 's/^v//')
describe_items=($(echo $gitDescribe | tr '-' ' '))
echo $describe_items
describe_len=${#describe_items[@]}
VERSION=${describe_items[0]}
if [ $describe_len -ge 3 ];then
    buildRelease=${describe_items[1]}.${describe_items[2]}
else
    buildRelease=0
fi

branch_info=($(git branch | grep '^*' | cut -d ' ' -f 2 | tr '-' " "))
release_name=${branch_info[0]}
release_version=${branch_info[0]}

git_commit=$(git log -n 1 --pretty --format=%h)

action=$1

function build(){
    docker build -t $image_name:$release_version-$buildRelease-$git_commit .
}

function push(){
    docker push $image_name:$release_version-$buildRelease-$git_commit
}

function test(){
    docker run -itd --name blog -p 9090:9090 $image_name:$release_version-$buildRelease-$git_commit
}

case $action in
    build)
        build
    ;;
    test)
        build

    ;;
    push)
        push
    ;;
    *)
        build
        push
    ;;
esac