<?php
namespace app\index\controller;
use app\index\model\Video;

class IndexController extends \think\Controller
{
    public function index()
    {

        return $this->fetch();
    }
    //分类排行榜
    public function rank($category) {
        $data = Video::all(
            function($query)use($category){
                $query->where('category','=',$category)->order('score','desc')->limit(10);
            });

        $this->assign('data',$data);
        $this->assign('category',$category);
        return $this->fetch();
    }
}
