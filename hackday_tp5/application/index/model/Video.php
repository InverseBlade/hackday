<?php
/**
 * Created by PhpStorm.
 * User: Dell
 * Date: 2017/11/18
 * Time: 13:49
 */
namespace app\index\model;
use think\Model;

class Video extends Model {

    public function getIntroductAttr($value) {
        if($value == 'None' or $value == 'none'){
            return "暂时没有简介哦~";
        }else{
            return $value;
        }
    }
}