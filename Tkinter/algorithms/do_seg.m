function cmtime_cmp=do_seg(W,K,seeds,labels,alpha,N)
I = sparse(1:N,1:N,ones(N,1)); 
D_inv = sparse(1:N,1:N,1./sum(W));
lines = zeros(N,K);
for k=1:K,
    label_idx = find(labels(:)==k);     %找到label=1的元素的位置
    Mk = size(label_idx,1);             %返回矩阵label_idx的行数
    lines(seeds(label_idx(:)),k) = 1/Mk;%average of probabilities,lines=1/Mk*blk
    clear label_idx;
end;
iD_inv=sqrt(D_inv);
S=iD_inv*W*iD_inv; 
cmtime_cmp=(I-alpha*S)\lines;
end