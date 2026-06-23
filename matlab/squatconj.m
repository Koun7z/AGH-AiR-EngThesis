function [ n ] = squatconj( q )
%squatconj Compute the conjugate of a quaternion
%  
    [rq,cq] = size(q);

    if(rq ~= 4 || cq ~=1)
        error("Input quaternion must be a 4 element column vector");
    end
    
    
    n = [q(1); -q(2); -q(3); -q(4)];

end