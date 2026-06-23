function [ n ] = squatmul( p, q )
%squatmultiply Symbolic quaternion multiplication
    
    [rq,cq] = size(q);
    [rr,cr] = size(p);

    if(rq ~= 4 || cq ~=1)
        error("Input quaternion must be a 4 element column vector");
    end

    if(rr ~= 4 || cr ~=1)
        error("Input quaternion must be a 4 element column vector");
    end
    

     n = [(p(1)*q(1) - p(2)*q(2) - p(3)*q(3) - p(4)*q(4));
          (p(1)*q(2) + p(2)*q(1) + p(3)*q(4) - p(4)*q(3));
          (p(1)*q(3) - p(2)*q(4) + p(3)*q(1) + p(4)*q(2));
          (p(1)*q(4) + p(2)*q(3) - p(3)*q(2) + p(4)*q(1))];
end