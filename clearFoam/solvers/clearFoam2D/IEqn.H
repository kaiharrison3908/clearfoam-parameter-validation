// implementation of enzyme production from gene circuit model
tmp<volScalarField> Q2 =
    (K_1*K_1/4 * A*A * R2_TOT) / (1.0+K_1 * A + K_1*K_1/4 *A*A+ SMALL);


fvScalarMatrix IEqn
(
    fvm::ddt(I)
  ==
    (beta_lux + ((alpha_lux - beta_lux)/(1.0+(K_lux / (Q2 + epsilon)))) 
    - gamma_I * I - K_I * I) * regionMask * D_enzyme
);

solve(IEqn);
