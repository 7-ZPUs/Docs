import { Routes } from '@angular/router';
 
export const APP_ROUTES: Routes = [
  {
    path: '',
    redirectTo: 'dip-explorer',
    pathMatch: 'full',
  },
  {
    path: 'dip-explorer',
    loadComponent: () =>
      import('./features/dip-explorer/ui/smart/dip-loading-page.component')
        .then(m => m.DipLoadingPageComponent),
  },
  {
    path: 'search',
    loadComponent: () =>
      import('./features/search/ui/smart/search-page.component')
        .then(m => m.SearchPageComponent),
  },
  {
    path: 'verification',
    loadComponent: () =>
      import('./features/verification/ui/smart/verification-page.component')
        .then(m => m.VerificationPageComponent),
  },
  {
    path: 'export-manager',
    loadComponent: () =>
      import('./features/export-manager/ui/smart/export-page.component')
        .then(m => m.ExportPageComponent),
  },
  {
    path: '**',
    redirectTo: 'dip-explorer',
  },
];