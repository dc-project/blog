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

function prepare() {
    if [[ "$(docker ps -a | wc -l)" -gt 1 ]];then
        docker ps -a | grep blog | cut -d ' ' -f 1 | xargs docker rm -f
    fi
}

function build(){
    docker build --no-cache -t $image_name:$release_version-$buildRelease .
}

function push(){
    docker push $image_name:$release_version-$buildRelease
}

function test(){
    docker run -itd --name blog -p 9090:9090 --network host $image_name:$release_version-$buildRelease
}

case $action in
    build)
        prepare
        build
    ;;
    test)
        prepare
        build
        test
    ;;
    local_test)
        test
    ;;
    push)
        push
    ;;
    *)
        build
        push
    ;;
esac