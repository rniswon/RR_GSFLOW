    MODULE STAGEMODULE
    DOUBLE PRECISION, SAVE, DIMENSION(:), POINTER :: stage
    DOUBLE PRECISION, SAVE, DIMENSION(:), POINTER :: volume
    END MODULE STAGEMODULE
    
    PROGRAM STAGECALC
    USE STAGEMODULE
    IMPLICIT NONE
    CHARACTER(LEN=200)::LINE
    CHARACTER(LEN=10)::TIME
    CHARACTER(LEN=1)::CHECK
    INTEGER :: LLOC, ISTART, ISTOP, I, ii, IOSTAT
    REAL :: VOL2, STG, R
    DOUBLE PRECISION :: VOL
    EXTERNAL :: STGTERP
    DOUBLE PRECISION :: STGTERP
    
    Open(2,file='mendovol.dat')
    Open(3,file='sonomavol.dat')
    Open(4,file='meno_bathy.dat')
    Open(5,file='Sonoma_bathy.dat')
    Open(6,file='output.dat')
    Open(7,file='mendo.out')
    Open(8,file='sonoma.out')
    allocate(stage(151),volume(151))
    stage = 0.0
    volume = 0.0
    ii=1
    do 300
        read(4,'(A)', IOSTAT=iostat) line
        if( iostat < 0 ) exit
        LLOC = 1
        CALL URWORD(LINE, LLOC, ISTART, ISTOP, 1, I, R, 6, 4)
        IF ( LINE(ISTART:ISTART) == "#" ) GOTO 300
        IF ( LINE(ISTART:ISTART) == "" ) exit
        LLOC = 1
        CALL URWORD(LINE, LLOC, ISTART, ISTOP, 3, I, STG, 6, 4)
        CALL URWORD(LINE, LLOC, ISTART, ISTOP, 3, I, VOL2, 6, 4)
        STAGE(ii) = STG
        VOLUME(ii) = VOL2
        ii = ii + 1
300 end do
    
    ii=1
    write(7,*)'Date Volume Stage'
    do 400
        read(2,'(A)', IOSTAT=iostat) line
        if( iostat < 0 ) exit
        LLOC = 1
        CALL URWORD(LINE, LLOC, ISTART, ISTOP, 1, I, R, 6, 2)
        IF ( LINE(ISTART:ISTART) == "#" ) GOTO 400
        IF ( LINE(ISTART:ISTART) == "" ) exit
        LLOC = 1
        CALL URWORD(LINE, LLOC, ISTART, ISTOP, 1, I, R, 6, 2)
        TIME = LINE(ISTART:ISTOP)
        CALL URWORD(LINE, LLOC, ISTART, ISTOP, 3, I, VOL2, 6, 2)
        VOL = VOL2
        STG = STGTERP (VOL)
        WRITE(7,*) TIME, VOL, STG
        ii = ii + 1
400  end do 
!  Sonoma
    stage = 0.0
    volume = 0.0
    ii=1
    do 100
        read(5,'(A)', IOSTAT=iostat) line
        if( iostat < 0 ) exit
        LLOC = 1
        CALL URWORD(LINE, LLOC, ISTART, ISTOP, 1, I, R, 6, 5)
        IF ( LINE(ISTART:ISTART) == "#" ) GOTO 100
        IF ( LINE(ISTART:ISTART) == "" ) exit
        LLOC = 1
        CALL URWORD(LINE, LLOC, ISTART, ISTOP, 3, I, STG, 6, 5)
        CALL URWORD(LINE, LLOC, ISTART, ISTOP, 3, I, VOL2, 6, 5)
        STAGE(ii) = STG
        VOLUME(ii) = VOL2
        ii = ii + 1
100    end do
    
    ii=1
    write(8,*)'Date Volume Stage'
    do 200
        read(3,'(A)', IOSTAT=iostat) line
        if( iostat < 0 ) exit
        LLOC = 1
        CALL URWORD(LINE, LLOC, ISTART, ISTOP, 1, I, R, 6, 3)
        IF ( LINE(ISTART:ISTART) == "#" ) GOTO 200
        IF ( LINE(ISTART:ISTART) == "" ) exit
        LLOC = 1
        CALL URWORD(LINE, LLOC, ISTART, ISTOP, 1, I, R, 6, 3)
        TIME = LINE(ISTART:ISTOP)
        CALL URWORD(LINE, LLOC, ISTART, ISTOP, 3, I, VOL2, 6, 3)
        VOL = VOL2
        STG = STGTERP (VOL)
        WRITE(8,*) TIME, VOL, STG
        ii = ii + 1
200    end do 
    DEALLOCATE(stage)
    DEALLOCATE(volume)
    end program
        
    DOUBLE PRECISION FUNCTION STGTERP (VOL)
!     FUNCTION LINEARLY INTERPOLATES BETWEEN TWO VALUES
!          OF LAKE VOLUME TO CACULATE LAKE STAGE.
      USE STAGEMODULE
      IMPLICIT NONE
      DOUBLE PRECISION VOL, TOLF2, FOLD
      DOUBLE PRECISION D1, D2, V1, V2, SLOPE
      INTEGER LN, I
!!      DOUBLE PRECISION VOLUME, STAGE
      TOLF2=1.0E-7
      STGTERP = 0.0D0
      IF (VOL.GT.volume(151))THEN
        D1 = stage(150)
        D2 = stage(151)
        V1 = volume(150)
        V2 = volume(151)
        SLOPE = (D2-D1)/(V2-V1)
        STGTERP =  SLOPE*VOL+D2-SLOPE*V2
        RETURN
      END IF
      I = 1
      DO
        D1 = stage(I)
        D2 = stage(I+1)
        V1 = volume(I)
        V2 = volume(I+1)
        SLOPE = (D2-D1)/(V2-V1)
        FOLD = VOL-V1    
        IF (FOLD .LE. 0.0d0) THEN  
          STGTERP=D1
          EXIT
        ELSEIF (VOL.GE.V1 .AND. VOL.LE.V2)THEN
          STGTERP =  SLOPE*VOL+D2-SLOPE*V2                 
          EXIT
        END IF
        I = I + 1
        IF( I.GT.150 ) THEN 
          STGTERP =  SLOPE*VOL+D2-SLOPE*V2
          EXIT
        END IF
      END DO
      RETURN
      END FUNCTION STGTERP