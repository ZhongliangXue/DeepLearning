% function [ output_args ] = demo_LazyRWSuperpixel( input_args )
% DEMO Summary of this function goes here

% clear all;
close all;
addpath('algorithms');
addpath('mex');
% matlabpool local 4
% maxNumCompThreads(8);
% setenv('OMP_NUM_THREADS', '8');

%% parameter setting
Nsp=200; %num of sp
Thres=1.35; %threshold for split
beta=30; %gaussian parameter 
alpha=0.9992; %Lazy parameter

iteration = importdata('./test/iteration.txt');
nItrs_max = iteration;% limit for the number of iterations

data = importdata('./test/myfile.txt');
img = imread(strcat('./test/image1/P1-',num2str(data),'.png'));
img = imresize(img,1);%0.25表示输出图像的每个边的变为原来的1/4，当设置为1时图像保持为原图的大小
img=im2double(img);
[X,Y,Z]=size(img);
gray_img=rgb2gray(img);

%% seed generate
N_init = round(Nsp/4); % initialize the number of seed to 1/4 of target seeds number
expSuperPixelDist = sqrt(numel(gray_img)/N_init);
normSigma = floor(expSuperPixelDist / 2.5);
[speed] = get_speed_based_on_gradient(gray_img,normSigma); %used for seeds relocate
% Place initial seeds and compute the initial signed distanece 
seeds = get_initial_seeds(gray_img, N_init, speed);
%% energy optimize
tic
[label_img, center_points, ~]=energy_opt(img,seeds,alpha,beta,Thres, Nsp, nItrs_max);
disp(['total time elapsed:' num2str(toc)]);
%% results of each image
[bmap] = seg2bmap(label_img,Y,X);

idx = find(bmap>0);
bmapOnImg = img(:,:,1);
bmapOnImg(idx) = 1;

if Z==3
    temp=img(:,:,2);
    temp(idx)=0;
bmapOnImg(:,:,2) = temp;
    temp=img(:,:,3);
    temp(idx)=0;
bmapOnImg(:,:,3) = temp;
end

%     figure('name','bmap');imshow(bmapOnImg);
imwrite(bmapOnImg,strcat('./test/image2/result_PET_',num2str(data),'.bmp'));
imwrite(bmapOnImg(:,:,1),strcat('./test/used_image/result_PET1_',num2str(data),'.bmp'));
%将矩阵值从0-1之间对应到0-255之间
imwrite(im2uint8(gray_img),strcat('./test/used_image/result_gray_img_',num2str(data),'.bmp'));
imwrite(uint8(label_img),strcat('./test/used_image/result_label_img_',num2str(data),'.bmp'));
    %% 将需要的数据可以保存出来
    %将最终生成的中心点的坐标保存到txt文件中
    % f = fopen('gray_img.txt','wt');
    % tmp = gray_img;
    % fprintf(f,'%f\n',tmp);
    % fclose(f);