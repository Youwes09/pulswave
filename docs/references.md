# References

The PDFs are kept in `resources/`, which is not tracked.

## Baselines and methodology

1. W. Wang, Z. Hu, P. Zhang. Liquid-fueled oblique detonation waves induced by reactive and non-reactive transverse liquid jets. *Aerosp. Sci. Technol.* 168 (2026) 111293. arXiv:2506.15247. Open-wedge baseline reproduced here.
2. W. Wang, Z. Hu, P. Zhang. Liquid-fueled oblique detonation stabilized by a transverse jet. arXiv:2605.27871. Confined-combustor baseline.
3. Z. Jiang, Z. Chen, L. Shi, Z. Zhang, J. Hao, C.-Y. Wen. Numerical study of oblique detonation initiation assisted by local energy deposition. arXiv:2508.08943. Pulsed-actuation methodology and f_cri.

## Validation and model settings

4. H. Guo, Y. Xu, H. Zheng, H. Zhang. Ignition limit and shock-to-detonation transition mode of n-heptane/air mixture in high-speed wedge flows. arXiv:2202.04987. Premixed ODW validation case.
5. W. Wang, M. Yang, Z. Hu, P. Zhang. A dynamic droplet breakup model for Eulerian–Lagrangian simulation of liquid-fueled detonation. arXiv:2404.03170. The baseline authors' solver and spray settings.
6. W. Wang, Z. Hu, P. Zhang. Computational investigation on the formation of liquid-fueled oblique detonation waves. arXiv:2407.17714. Initiation-length definition and evaporative-cooling behaviour.
7. H. Guo, Y. Xu, N. Zhao, H. Zhang. Autoignition of two-phase n-heptane/air mixtures behind an oblique shock: insights into spray oblique detonation initiation. arXiv:2212.07550.
8. H. Guo, Y. Xu, S. Li, H. Zhang. On the evolutions of induction zone structure in wedge-stabilized oblique detonation with water mist flows. arXiv:2201.03934.
9. Z. Huang, M. Zhao, Y. Xu, G. Li, H. Zhang. Eulerian–Lagrangian modelling of detonative combustion in two-phase gas–droplet mixtures with OpenFOAM: validations and verifications. arXiv:2009.09596.

## Liquid jets in supersonic crossflow

These were used to decide how to represent the jet.

10. Y. Zhou, Z. Cai, Q. Li, C. Li, M. Sun, P. Li, H. Wang. Review of atomization mechanism and spray characteristics of a liquid jet in supersonic crossflow. *Chin. J. Aeronaut.* 36(8) (2023) 1–23.
11. T.-W. Lee, J. E. Park. Determination of the drop size during atomization of liquid jets in cross flows. arXiv:1804.05973.
12. M. V. V. Srinivas, A. K. Rajagopal, B. Lebonah, M. Jegesh David. Internal aerodynamics of supersonic crossflows with transverse liquid injection. arXiv:2502.09295.
13. M. Ullman, S. Sharma, V. Raman. Numerical simulation of reacting and non-reacting liquid jets in supersonic crossflow. arXiv:2504.15422.
14. C. Medipati, S. Deivandren, R. N. Govardhan. Elliptical liquid jets in a supersonic cross-flow: influence of J on atomization mechanism and unsteadiness. arXiv:2512.23360.
15. A. Sinha. Liquid jet in crossflow: review of breakup modes and injector geometry effects. arXiv:2606.25125.

## Solver, chemistry and software

16. J. Sun, Y. Wang, B. Tian, Z. Chen. detonationFoam: an open-source solver for simulation of gaseous detonation based on OpenFOAM. *Comput. Phys. Commun.* 292 (2023) 108859. Code: github.com/JieSun-pku/detonationFoam, branch `detonationFoam-dev(two-phase)`.
17. S. Liu, J. C. Hewson, J. H. Chen, H. Pitsch. Effects of strain rate on high-pressure nonpremixed n-heptane autoignition in counterflow. *Combust. Flame* 137 (2004) 320–339. The chemistry mechanism.
18. OpenFOAM-8, The OpenFOAM Foundation. github.com/OpenFOAM/OpenFOAM-8.
19. Cantera 3.2.0. cantera.org.
