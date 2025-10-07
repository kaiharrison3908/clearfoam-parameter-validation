
dimensionedScalar Dn_bulk (
    "Dn_bulk",
    dimensionSet(0, 2, -1, 0, 0, 0, 0),
    0.0001 / 86400 
);
dimensionedScalar Dn_biofilm (
    "Dn_biofilm",
    dimensionSet(0, 2, -1, 0, 0, 0, 0),
    0.00002  / 86400    
);

tmp<volScalarField> Dntmp = Dn_bulk*(1.0 - min(E, scalar(1.0))) + Dn_biofilm*(min(E, scalar(1.0)));

volScalarField Dn
(
    IOobject
    (
        "Dn",                    
        runTime.timeName(),     
        mesh,                  
        IOobject::NO_READ,      
        IOobject::AUTO_WRITE
    ),
    Dntmp                        
);

volScalarField hill_N = pow(A, n) / (pow(tau, n) + pow(A, n));

fvScalarMatrix NEqn
(
    fvm::ddt(N)
    - fvm::laplacian(Dn, N, "laplacian(Dn,N)")
    == 
    eta1 * hill_N * M
    + fvm::Sp(mu*C/(k_1+C), N)
    - fvm::Sp(k_4, N)
    - fvm::Sp(eta2*M/(k5+M), N)
    + eta_disp * delta_death*max(scalar(0), (E_crit - E)/E_crit) * switchField * M
    
);

solve(NEqn);
