

const bool adjustTimeStep =
runTime.controlDict().getOrDefault("adjustTimeStep", false);

scalar maxDeltaT =
runTime.controlDict().getOrDefault<scalar>("maxDeltaT", GREAT);

const scalar truncationError_global =
runTime.controlDict().lookupOrDefault<scalar>("truncationError",0.01);

const scalar truncationError_C =
runTime.controlDict().lookupOrDefault<scalar>("truncationError_C",truncationError_global);

const scalar truncationError_M =
runTime.controlDict().lookupOrDefault<scalar>("truncationError_M",truncationError_global);

const scalar truncationError_A =
runTime.controlDict().lookupOrDefault<scalar>("truncationError_A",truncationError_global);

const scalar truncationError_N =
runTime.controlDict().lookupOrDefault<scalar>("truncationError_N",truncationError_global);

const scalar truncationError_E =
runTime.controlDict().lookupOrDefault<scalar>("truncationError_E",truncationError_global);

const scalar truncationError_I =
runTime.controlDict().lookupOrDefault<scalar>("truncationError_I",truncationError_global);

const scalar truncationError_Ie =
runTime.controlDict().lookupOrDefault<scalar>("truncationError_Ie",truncationError_global);

timestepManager dtManagerC(runTime, C, truncationError_C);
timestepManager dtManagerM(runTime, M, truncationError_M);
timestepManager dtManagerA(runTime, A, truncationError_A);
timestepManager dtManagerN(runTime, N, truncationError_N);
timestepManager dtManagerE(runTime, E, truncationError_E);
timestepManager dtManagerI(runTime, I, truncationError_I);
timestepManager dtManagerIe(runTime, Ie, truncationError_Ie);

// ************************************************************************* //
