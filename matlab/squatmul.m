function [ n ] = squatmul( q,r )
%squatmultiply Symbolic quaternion multiplication
    
    [rq,cq] = size(q);
    [rr,cr] = size(r);

    if(rq ~= 4 || cq ~=1)
        error("Input quaternion must be a 4 element column vector");
    end

    if(rr ~= 4 || cr ~=1)
        error("Input quaternion must be a 4 element column vector");
    end
    

     n = [(r(1)*q(1)-r(2)*q(2)-r(3)*q(3)-r(4)*q(4));
          (r(1)*q(2)+r(2)*q(1)-r(3)*q(4)+r(4)*q(3));
          (r(1)*q(3)+r(2)*q(4)+r(3)*q(1)-r(4)*q(2));
          (r(1)*q(4)-r(2)*q(3)+r(3)*q(2)+r(4)*q(1))];
end